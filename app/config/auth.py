import httpx
import jwt
from typing import Optional
from fastapi_oidc import get_auth
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials, HTTPBearer,
    SecurityScopes, APIKeyHeader
)
from fastapi_third_party_auth import Auth, GrantType, IDToken
from pydantic import ValidationError

from app.config.config import configuration as cfg
from app.config.logging import create_logger


logger = create_logger(name="app.config.client")

class OpenAMIDToken(IDToken):
    tipo_utente: Optional[str] = None
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    iv_pg_codfis: Optional[str] = None
    iv_pg_piva: Optional[str] = None
    iv_codfis: Optional[str] = None
    iv_tipoutente: Optional[str] = None
    token_type: Optional[str] = None
    tokenType: Optional[str] = None

class CustomAuth(Auth):
    CAMPO_TIPO_UTENTE = "iv_tipoutente"
    CF_PERSONA_FISICA = "sub"
    CF_PERSONA_GIURIDICA = "iv_pg_codfis"
    PARTITA_IVA = "iv_pg_piva"
    ID_TOKEN_TYPE = "JWTToken"
    ACCESS_TOKEN_TYPE = "Bearer"

    def __init__(self, openid_userinfo_url: str, **kwargs):
        self.openid_userinfo_url=openid_userinfo_url
        super().__init__(**kwargs)

    async def authorized(
        self,
        security_scopes: SecurityScopes,
        authorization_credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer()
        ),
    ) -> OpenAMIDToken:
        """Validate and parse OIDC ID token against configuration.
        Note this function caches the signatures and algorithms of the issuing
        server for signature_cache_ttl seconds.
        Args:
            security_scopes (SecurityScopes): Security scopes
            auth_header (str): Base64 encoded OIDC Token. This is invoked
                behind the scenes by Depends.
        Return:
            OpenAMIDToken (self.idtoken_model): User information included
                `tipo_utente`
        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
            HTTPException(status_code=403, detail=f"Forbidden: {err}")
            IDToken validation errors
        """

        id_token = self.required(
            security_scopes,
            authorization_credentials
        )

        if id_token is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        else:
            userinfo = httpx.get(
                self.openid_userinfo_url,
                headers={
                    "Authorization": f"{authorization_credentials.scheme} {authorization_credentials.credentials}"
                }
            )
            user_type = userinfo.json().get(self.CAMPO_TIPO_UTENTE)
            id_token = OpenAMIDToken(**id_token.dict())
            id_token.tipo_utente = user_type
            if cfg.SISCAT_WHITELIST_DIPENDENTE:
                if id_token.sub in cfg.SISCAT_WHITELIST_DIPENDENTE.split(","):
                    id_token.tipo_utente = "dipendente"
            if id_token.tipo_utente == "dipendente":
                return id_token
            else:
                logger.error("L'utente non ha un profilo DIPENDENTE");
                raise HTTPException(status.HTTP_403_FORBIDDEN)


    async def citizen_authorized(
        self,
        authorization_credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer()
        ),
    ) -> OpenAMIDToken:
        """Validate and parse OIDC ID token against configuration.
        Note this function caches the signatures and algorithms of the issuing
        server for signature_cache_ttl seconds.
        Args:
            security_scopes (SecurityScopes): Security scopes
            auth_header (str): Base64 encoded OIDC Token. This is invoked
                behind the scenes by Depends.
        Return:
            OpenAMIDToken (self.idtoken_model): User information included
                `tipo_utente`
        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
            HTTPException(status_code=403, detail=f"Forbidden: {err}")
            IDToken validation errors
        """

        token = authorization_credentials.credentials
        try:
            id_token = jwt.decode(token, options={"verify_signature": False})
        except jwt.exceptions.DecodeError as err:
            logger.error(f"Token decode error: {err}")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if id_token is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        else:
            userinfo = httpx.get(
                self.openid_userinfo_url,
                headers={
                    "Authorization": f"{authorization_credentials.scheme} {authorization_credentials.credentials}"
                }
            )
            user_type = userinfo.json().get(self.CAMPO_TIPO_UTENTE)
            id_token = OpenAMIDToken(**id_token)
            id_token.tipo_utente = user_type
            codice_fiscale = userinfo.json().get(self.CF_PERSONA_FISICA)
            id_token.codice_fiscale = codice_fiscale
            if cfg.SISCAT_WHITELIST_DIPENDENTE:
                if id_token.sub in cfg.SISCAT_WHITELIST_DIPENDENTE.split(","):
                    id_token.tipo_utente = "cittadino"
            if id_token.tipo_utente == "cittadino":
                return id_token
            else:
                logger.error("L'utente non ha un profilo DIPENDENTE");
                raise HTTPException(status.HTTP_403_FORBIDDEN)

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in cfg.CUSTOM_APIKEYS.split(','):
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

oauth_scope = []
if(cfg.OPENAM_SCOPES):
    oauth_scope = cfg.OPENAM_SCOPES.split(',')

    if not oauth_scope:
        oauth_scope = []

auth = CustomAuth(
    openid_connect_url=f"{cfg.OPENAM_OIDC_BASE_URL}{cfg.OPENAM_OIDC_WELL_KNOWN_CONTEXT}",  # noqa
    openid_userinfo_url=cfg.OPENAM_OIDC_USERINFO_URL,
    # issuer=f"{cfg.OPENAM_OIDC_BASE_URL}",
    client_id=cfg.OPENAM_CLIENT_ID,  # optional, verification only
    scopes=oauth_scope,#["profile", "openid", "persona_giuridica"], #scopes=["openid", "tipo_utente"],  # optional, verification only
    grant_types=[GrantType.AUTHORIZATION_CODE],  # optional, docs only
    idtoken_model=OpenAMIDToken,  # optional, verification only
)
