import logging
from math import log

import joblib
import numpy

from .sql import GB_SELECT_APP, INSERT_SCORE

logger = logging.getLogger('gradient_boosting')


class GradientBoosting:
    REPLACE = {'true': True, 'false': False, None: numpy.nan}

    FEATURES_CONT = ['gender', 'user_agent_device', 'age', 'seon_accounts_exist_count',
                     'iov_device_firstseen_delta_hours', 'company_phone_length', 'company_name_lower',
                     'job_position_lower', 'default_loan_limit', 'job_position_id_v2', 'company_name_id_v2',
                     'email_length_before_at', 'iov_dots_resolution', 'account_exists', 'trade_bureau_count',
                     'enquiry_count', 'risk_grade', 'borrower_total_limit', 'existing_facility_count',
                     'counts_of_credits', 'avg_payed1', 'facility_cards', 'count_of_0cp2', 'avg_payed8',
                     'total_outstanding_balance_sum', 'total_istallment', 'salary', 'hotkeys_sum',
                     'iov_device_cookie_enabled', 'iov_device_flash_installed', 'iov_device_new',
                     'mobile_phone_resend_tries', 'seon_email_score', 'seon_account_number_of_breaches']

    FEATURES_CAT = ['social_status_id', 'bank_id', 'work_living_time', 'working_industry_id', 'loan_purpose',
                    'relative_type', 'living_time', 'marital_status', 'whatsapp_exists', 'account_facebook_exists',
                    'account_google_exists', 'account_twitter_exists', 'account_apple_exists',
                    'account_microsoft_exists', 'account_yahoo_exists', 'account_instagram_exists',
                    'account_spotify_exists', 'account_linkedin_exists']

    FEATURES_CAT_TEXT = ['mobile_operator', 'domain', 'iov_device_browser_lang', 'iov_device_browser_type',
                         'iov_device_type']

    LIST_BANK_ID = [569, 568, 560, 565, 557, 551, 549, 550, 555]
    FILL_BANK_ID = 998
    LIST_DOMAIN = ['yahoo.com', 'yahoo.com.my', 'ymail.com', 'hotmail.com', 'gmail.com', 'icloud.com']
    FILL_DOMAIN = 'OTHER'
    LIST_LANG = ['EN-GB', 'EN-MY', 'EN-US', 'EN-AU', 'MS-MY', 'ZH-CN', 'MS']
    FILL_LANG = 'OTHER'
    LIST_BROWSER = ['FIREFOX', 'SAFARI', 'MOBILE', 'SAMSUNGBROWSER', 'CHROME', 'VIVOBROWSER', 'UCBROWSER']
    FILL_BROWSER = 'OTHER'
    LIST_SOCIAL_STATUS_ID = [2, 3, 4, 8, 11, 12, 13, 14, 15]
    FILL_SOCIAL_STATUS_ID = 998
    LIST_WORK_LIVING_TIME = [1, 2, 3, 4]
    FILL_WORK_LIVING_TIME = 998
    LIST_WORKING_INDUSTRY_ID = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
    FILL_WORKING_INDUSTRY_ID = 998
    LIST_IOV_DEVICE_TYPE = ['ANDROID', 'HANDHELD_OTHER', 'IPAD', 'IPHONE', 'LINUX', 'MAC', 'NAN', 'WINDOWS']
    FILL_IOV_DEVICE_TYPE = 'NAN'
    LIST_LOAN_PURPOSE = [1, 2, 3, 4, 5]
    FILL_LOAN_PURPOSE = 2
    LIST_RELATIVE_TYPE = [1, 2, 3, 4, 5, 6, 7, 8]
    FILL_RELATIVE_TYPE = 2
    LIST_LIVING_TIME = [1, 2, 3, 4]
    FILL_LIVING_TIME = 2
    LIST_MARITAL_STATUS = [1, 2, 3, 4, 999]
    FILL_MARITAL_STATUS = 999
    LIST_WHATSAPP_EXISTS = [0, 1, 998, 999]
    FILL_WHATSAPP_EXISTS = 998
    LIST_ACCOUNT_FACEBOOK_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_FACEBOOK_EXISTS = 999
    LIST_ACCOUNT_GOOGLE_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_GOOGLE_EXISTS = 999
    LIST_ACCOUNT_TWITTER_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_TWITTER_EXISTS = 999
    LIST_ACCOUNT_APPLE_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_APPLE_EXISTS = 999
    LIST_ACCOUNT_MICROSOFT_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_MICROSOFT_EXISTS = 999
    LIST_ACCOUNT_YAHOO_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_YAHOO_EXISTS = 999
    LIST_ACCOUNT_INSTAGRAM_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_INSTAGRAM_EXISTS = 999
    LIST_ACCOUNT_SPOTIFY_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_SPOTIFY_EXISTS = 999
    LIST_ACCOUNT_LINKEDIN_EXISTS = [0, 1, 998, 999]
    FILL_ACCOUNT_LINKEDIN_EXISTS = 999
    LIST_MOBILE_OPERATOR = ['Celcom', 'DiGi', 'Maxis', 'Other', 'Tune Talk', 'U Mobile', 'Yes 4G']
    FILL_MOBILE_OPERATOR = 'Other'

    def __init__(self, application):
        self.lgbm_model = joblib.load('application/assets/model_lgbm.pkl')
        self.encoder = joblib.load('application/assets/encoder.pkl')
        self.app = application

    def verify_application(self, value):
        return self.REPLACE.get(value, value)

    def execute(self, app_id):
        application = self.app.get_data_from_web_db(
            GB_SELECT_APP.format(app_id=app_id)
        )
        if application is not None and application.empty:
            print(f'Application {app_id} not found.')
        else:
            print(f'Application {app_id}: start verify')
            application = application.applymap(lambda x: self.verify_application(x))

            # input empty values
            application[self.FEATURES_CONT] = application[self.FEATURES_CONT].fillna(-99).astype(float)
            application[self.FEATURES_CAT] = application[self.FEATURES_CAT].fillna(999).astype(int)
            application[self.FEATURES_CAT_TEXT] = application[self.FEATURES_CAT_TEXT].fillna('NAN')

            # delete question by category
            application['bank_id'][application.bank_id.isin(self.LIST_BANK_ID) == False] = self.FILL_BANK_ID
            application['domain'][application.domain.isin(self.LIST_DOMAIN) == False] = self.FILL_DOMAIN
            application['iov_device_browser_lang'][
                application.iov_device_browser_lang.isin(self.LIST_LANG) == False] = self.FILL_LANG
            application['iov_device_browser_type'][
                application.iov_device_browser_type.isin(self.LIST_BROWSER) == False] = self.FILL_BROWSER

            # delete class not in model
            application['social_status_id'][application.social_status_id.isin(self.LIST_SOCIAL_STATUS_ID) == False] = self.FILL_SOCIAL_STATUS_ID
            application['work_living_time'][application.work_living_time.isin(self.LIST_WORK_LIVING_TIME) == False] = self.FILL_WORK_LIVING_TIME
            application['working_industry_id'][application.working_industry_id.isin(self.LIST_WORKING_INDUSTRY_ID) == False] = self.FILL_WORKING_INDUSTRY_ID
            application['iov_device_type'][application.iov_device_type.isin(self.LIST_IOV_DEVICE_TYPE) == False] = self.FILL_IOV_DEVICE_TYPE
            application['loan_purpose'][application.loan_purpose.isin(self.LIST_LOAN_PURPOSE) == False] = self.FILL_LOAN_PURPOSE
            application['relative_type'][application.relative_type.isin(self.LIST_RELATIVE_TYPE) == False] = self.FILL_RELATIVE_TYPE
            application['living_time'][application.living_time.isin(self.LIST_LIVING_TIME) == False] = self.FILL_LIVING_TIME
            application['marital_status'][application.marital_status.isin(self.LIST_MARITAL_STATUS) == False] = self.FILL_MARITAL_STATUS
            application['whatsapp_exists'][application.whatsapp_exists.isin(self.LIST_WHATSAPP_EXISTS) == False] = self.FILL_WHATSAPP_EXISTS
            application['account_facebook_exists'][
                application.account_facebook_exists.isin(self.LIST_ACCOUNT_FACEBOOK_EXISTS) == False] = self.FILL_ACCOUNT_FACEBOOK_EXISTS
            application['account_google_exists'][
                application.account_google_exists.isin(self.LIST_ACCOUNT_GOOGLE_EXISTS) == False] = self.FILL_ACCOUNT_GOOGLE_EXISTS
            application['account_twitter_exists'][
                application.account_twitter_exists.isin(self.LIST_ACCOUNT_TWITTER_EXISTS) == False] = self.FILL_ACCOUNT_TWITTER_EXISTS
            application['account_apple_exists'][
                application.account_apple_exists.isin(self.LIST_ACCOUNT_APPLE_EXISTS) == False] = self.FILL_ACCOUNT_APPLE_EXISTS
            application['account_microsoft_exists'][
                application.account_microsoft_exists.isin(self.LIST_ACCOUNT_MICROSOFT_EXISTS) == False] = self.FILL_ACCOUNT_MICROSOFT_EXISTS
            application['account_yahoo_exists'][
                application.account_yahoo_exists.isin(self.LIST_ACCOUNT_YAHOO_EXISTS) == False] = self.FILL_ACCOUNT_YAHOO_EXISTS
            application['account_instagram_exists'][
                application.account_instagram_exists.isin(self.LIST_ACCOUNT_INSTAGRAM_EXISTS) == False] = self.FILL_ACCOUNT_INSTAGRAM_EXISTS
            application['account_spotify_exists'][
                application.account_spotify_exists.isin(self.LIST_ACCOUNT_SPOTIFY_EXISTS) == False] = self.FILL_ACCOUNT_SPOTIFY_EXISTS
            application['account_linkedin_exists'][
                application.account_linkedin_exists.isin(self.LIST_ACCOUNT_LINKEDIN_EXISTS) == False] = self.FILL_ACCOUNT_LINKEDIN_EXISTS
            application['mobile_operator'][application.mobile_operator.isin(self.LIST_MOBILE_OPERATOR) == False] = self.FILL_MOBILE_OPERATOR


            # generate features from encoder
            print(f'Application {app_id}: generate features from encoder')
            features_encoded = list(self.encoder.get_feature_names(self.FEATURES_CAT + self.FEATURES_CAT_TEXT))
            for i in features_encoded:
                application[i] = numpy.nan
            application[features_encoded] = self.encoder.transform(
                application[self.FEATURES_CAT + self.FEATURES_CAT_TEXT])
            features_in = self.FEATURES_CONT + features_encoded

            # run score
            print(f'Application {app_id}: run score')
            pd = self.lgbm_model.predict(application[features_in])[0]
            self.app.insert_to_web_db(INSERT_SCORE, (app_id, log(1 / pd - 1)))
