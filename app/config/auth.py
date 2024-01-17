import httpx
from typing import Callable, Optional
from fastapi_oidc import get_auth
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials, HTTPBearer,
    SecurityScopes, APIKeyHeader
)
from fastapi_third_party_auth import Auth, GrantType, IDToken

from app.config.config import configuration as cfg
from app.config.logging import create_logger


logger = create_logger(name="app.config.client")


OIDC_config = {
    "client_id": cfg.OPENAM_CLIENT_ID,
    # Audience can be omitted in which case the aud value defaults to client_id
    # "audience": "http://localhost:5000/api/v1",
    "base_authorization_server_uri": cfg.OPENAM_OIDC_BASE_URL,
    "issuer": cfg.OPENAM_OIDC_BASE_URL,
    "signature_cache_ttl": 3600,
}

authenticate_user: Callable = get_auth(**OIDC_config)

class OpenAMIDToken(IDToken):
    tipo_utente: Optional[str] = None
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    iv_pg_codfis: Optional[str] = None
    iv_pg_piva: Optional[str] = None


# auth = Auth(
#     openid_connect_url=f"{cfg.OPENAM_OIDC_BASE_URL}{cfg.OPENAM_OIDC_WELL_KNOWN_CONTEXT}",  # noqa
#     client_id=cfg.OPENAM_CLIENT_ID,  # optional, verification only
#     scopes=["openid", "tipo_utente"],  # optional, verification only
#     grant_types=[GrantType.AUTHORIZATION_CODE],  # optional, docs only
#     idtoken_model=OpenAMIDToken,  # optional, verification only
# )

class CustomAuth(Auth):
    CAMPO_TIPO_UTENTE = 'iv_tipoutente'
    CF_PERSONA_FISICA = 'sub'
    CF_PERSONA_GIURIDICA = 'iv_pg_codfis'
    PARTITA_IVA = 'iv_pg_piva'

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

            partita_iva = id_token.iv_pg_codfis
            cf_pgiuridica = id_token.iv_pg_piva
            user_type = None
            codice_fiscale = None
            if(not(partita_iva and cf_pgiuridica)):
                userinfo = httpx.get(
                    self.openid_userinfo_url,
                    headers={
                        "Authorization": f"{authorization_credentials.scheme} {authorization_credentials.credentials}"
                    }
                )
                user_type = userinfo.json().get(self.CAMPO_TIPO_UTENTE)
                codice_fiscale =  userinfo.json().get(self.CF_PERSONA_FISICA)
            id_token = OpenAMIDToken(**id_token.dict())
            id_token.tipo_utente = user_type
            if partita_iva and len(partita_iva.strip()) == 11:
                id_token.partita_iva = partita_iva
                return id_token
            elif cf_pgiuridica and len(cf_pgiuridica.strip()) == 11:
                id_token.partita_iva = cf_pgiuridica
                return id_token
            elif id_token.tipo_utente == "cittadino":
                id_token.codice_fiscale = codice_fiscale
                return id_token
            else:
                logger.error("L'utente non ha un profilo CITTADINO");
                raise HTTPException(status.HTTP_403_FORBIDDEN)

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in cfg.CUSTOM_APIKEYS.split(','):
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

oaut_scope = []
if(cfg.OPENAM_SCOPES):
    oaut_scope = cfg.OPENAM_SCOPES.split(',')

auth = CustomAuth(
    openid_connect_url=f"{cfg.OPENAM_OIDC_BASE_URL}{cfg.OPENAM_OIDC_WELL_KNOWN_CONTEXT}",  # noqa
    openid_userinfo_url=cfg.OPENAM_OIDC_USERINFO_URL,
    # issuer=f"{cfg.OPENAM_OIDC_BASE_URL}",
    client_id=cfg.OPENAM_CLIENT_ID,  # optional, verification only
    scopes=oaut_scope,#["profile", "openid", "persona_giuridica"], #scopes=["openid", "tipo_utente"],  # optional, verification only
    grant_types=[GrantType.AUTHORIZATION_CODE],  # optional, docs only
    idtoken_model=OpenAMIDToken,  # optional, verification only
)
