GB_SELECT_APP = """
    SELECT 
        abt.*,
        ap.salary,
        les.response::json -> 'data' -> 'account_details' -> 'facebook' ->> 'registered' as facebook_exists,
        les.response::json -> 'data' -> 'account_details' -> 'google' ->> 'registered' as google_exists,
        les.response::json -> 'data' -> 'account_details' -> 'whatsapp' ->> 'registered' as whatsapp_exists,
        les.response::json -> 'data' -> 'account_details' -> 'telegram' ->> 'registered' as telegram_exists,
        les.response::json -> 'data' -> 'account_details' -> 'viber' ->> 'registered' as viber_exists,
        ap.type,
        ap.living_time,
        ap.express_flag,        
        ap.marital_status,        
        ----------------------------------------------------applications
        cast(substring(ap.hotkeys_vector, 1, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 2, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 3, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 4, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 5, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 6, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 7, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 8, 1) as integer) +
        cast(substring(ap.hotkeys_vector, 9, 1) as integer) as hotkeys_sum,
        ap.mobile_phone_resend_tries, 
        iov.device_browser_type as iov_device_browser_type,
        iov.device_cookie_enabled as iov_device_cookie_enabled,
        iov.device_flash_installed as iov_device_flash_installed,
        iov.device_js_enabled as iov_device_js_enabled,
        iov.device_new as iov_device_new,
        iov.device_type as iov_device_type, 
        iov.ipaddress_loc_country as iov_ipaddress_loc_country, 
        iov.ipaddress_loc_region as iov_ipaddress_loc_region,
        seon.email_score as seon_email_score,
        seon.account_facebook_exists,
        seon.account_google_exists,
        seon.account_twitter_exists,
        seon.account_apple_exists,
        seon.account_microsoft_exists,
        seon.account_yahoo_exists,
        seon.account_instagram_exists,
        seon.account_spotify_exists,
        seon.account_linkedin_exists,
        seon.account_number_of_breaches as seon_account_number_of_breaches,
        seon.account_first_breach as seon_account_first_breach
    FROM public.applications as ap
        LEFT JOIN public.web_abt as abt on abt.application_id = ap.id
        LEFT JOIN public.log_external_services les on les.application_id = ap.id and data_source = 'Seon' and substring(les.response,2,9) = '"success"'
        LEFT JOIN public.application_iovations as iov on ap.id = iov.application_id
        LEFT JOIN public.application_seon_infos as seon on ap.id = seon.application_id and ap.email = seon.email
    WHERE
        ap.id = {app_id};
"""

INSERT_SCORE = """
    INSERT INTO risks.scores
    (application_id, score_value, score_type, score_data, created_at, updated_at)
    VALUES (%s, %s, 'APP_WEB_NEW_XGB_V001', null, now(), now());
"""