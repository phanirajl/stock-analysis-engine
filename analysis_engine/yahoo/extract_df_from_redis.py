"""
Extract an Yahoo dataset from Redis (S3 support coming soon) and
load it into a ``pandas.DataFrame``

Supported environment variables:

::

    # verbose logging in this module
    export DEBUG_EXTRACT=1

    # verbose logging for just Redis operations in this module
    export DEBUG_REDIS_EXTRACT=1

    # verbose logging for just S3 operations in this module
    export DEBUG_S3_EXTRACT=1

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json

"""

import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.dataset_scrub_utils as scrub_utils
import analysis_engine.get_data_from_redis_key as redis_get
import analysis_engine.yahoo.consts as yahoo_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def extract_pricing_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_pricing_dataset

    Extract the Yahoo pricing data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    label = work_dict.get('label', 'extract')
    ds_id = work_dict.get('ticker')
    df_type = yahoo_consts.DATAFEED_PRICING_YAHOO
    df_str = yahoo_consts.get_datafeed_str_yahoo(df_type=df_type)
    redis_key = work_dict.get(
        'redis_key',
        work_dict.get('pricing', 'missing-redis-key'))
    s3_key = work_dict.get(
        's3_key',
        work_dict.get('pricing', 'missing-s3-key'))
    redis_host = work_dict.get(
        'redis_host',
        None)
    redis_port = work_dict.get(
        'redis_port',
        None)
    redis_db = work_dict.get(
        'redis_db',
        ae_consts.REDIS_DB)

    log.debug(
        '{} - {} - start - redis_key={} s3_key={}'.format(
            label,
            df_str,
            redis_key,
            s3_key))

    if not redis_host and not redis_port:
        redis_host = ae_consts.REDIS_ADDRESS.split(':')[0]
        redis_port = ae_consts.REDIS_ADDRESS.split(':')[1]

    df = None
    status = ae_consts.NOT_RUN
    try:
        redis_rec = redis_get.get_data_from_redis_key(
            label=label,
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=work_dict.get('password', None),
            key=redis_key,
            decompress_df=True)

        status = redis_rec['status']
        log.debug(
            '{} - {} redis get data key={} status={}'.format(
                label,
                df_str,
                redis_key,
                ae_consts.get_status(status=status)))

        if status == ae_consts.SUCCESS:
            log.debug(
                '{} - {} redis convert pricing to json'.format(
                    label,
                    df_str))
            cached_dict = redis_rec['rec']['data']
            log.debug(
                '{} - {} redis convert pricing to df'.format(
                    label,
                    df_str))
            try:
                df = pd.DataFrame(
                    cached_dict,
                    index=[0])
            except Exception as f:
                log.debug(
                    '{} - {} redis_key={} '
                    'no pricing df found'.format(
                        label,
                        df_str,
                        redis_key))
                return ae_consts.EMPTY, None
            # end of try/ex to convert to df
            log.debug(
                '{} - {} redis_key={} done convert pricing to df'.format(
                    label,
                    df_str,
                    redis_key))
        else:
            log.debug(
                '{} - {} did not find valid redis pricing '
                'in redis_key={} status={}'.format(
                    label,
                    df_str,
                    redis_key,
                    ae_consts.get_status(status=status)))

    except Exception as e:
        log.debug(
            '{} - {} - ds_id={} failed getting pricing from '
            'redis={}:{}@{} key={} ex={}'.format(
                label,
                df_str,
                ds_id,
                redis_host,
                redis_port,
                redis_db,
                redis_key,
                e))
        return ae_consts.ERR, None
    # end of try/ex extract from redis

    log.debug(
        '{} - {} ds_id={} extract scrub={}'.format(
            label,
            df_str,
            ds_id,
            scrub_mode))

    scrubbed_df = scrub_utils.extract_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=df_type,
        msg_format='df={} date_str={}',
        ds_id=ds_id,
        df=df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of extract_pricing_dataset


def extract_yahoo_news_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_yahoo_news_dataset

    Extract the Yahoo news data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    label = work_dict.get('label', 'extract')
    ds_id = work_dict.get('ticker')
    df_type = yahoo_consts.DATAFEED_NEWS_YAHOO
    df_str = yahoo_consts.get_datafeed_str_yahoo(df_type=df_type)
    redis_key = work_dict.get(
        'redis_key',
        work_dict.get('news', 'missing-redis-key'))
    s3_key = work_dict.get(
        's3_key',
        work_dict.get('news', 'missing-s3-key'))
    redis_host = work_dict.get(
        'redis_host',
        None)
    redis_port = work_dict.get(
        'redis_port',
        None)
    redis_db = work_dict.get(
        'redis_db',
        ae_consts.REDIS_DB)

    log.debug(
        '{} - {} - start - redis_key={} s3_key={}'.format(
            label,
            df_str,
            redis_key,
            s3_key))

    if not redis_host and not redis_port:
        redis_host = ae_consts.REDIS_ADDRESS.split(':')[0]
        redis_port = ae_consts.REDIS_ADDRESS.split(':')[1]

    df = None
    status = ae_consts.NOT_RUN
    try:
        redis_rec = redis_get.get_data_from_redis_key(
            label=label,
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=work_dict.get('password', None),
            key=redis_key,
            decompress_df=True)

        status = redis_rec['status']
        log.debug(
            '{} - {} redis get data key={} status={}'.format(
                label,
                df_str,
                redis_key,
                ae_consts.get_status(status=status)))

        if status == ae_consts.SUCCESS:
            cached_dict = redis_rec['rec']['data']
            log.debug(
                '{} - {} redis convert news to df'.format(
                    label,
                    df_str))
            try:
                df = pd.DataFrame(
                    cached_dict)
            except Exception as f:
                log.debug(
                    '{} - {} redis_key={} '
                    'no news df found'.format(
                        label,
                        df_str,
                        redis_key))
                return ae_consts.EMPTY, None
            # end of try/ex to convert to df
            log.debug(
                '{} - {} redis_key={} done convert news to df'.format(
                    label,
                    df_str,
                    redis_key))
        else:
            log.debug(
                '{} - {} did not find valid redis news '
                'in redis_key={} status={}'.format(
                    label,
                    df_str,
                    redis_key,
                    ae_consts.get_status(status=status)))

    except Exception as e:
        log.debug(
            '{} - {} - ds_id={} failed getting news from '
            'redis={}:{}@{} key={} ex={}'.format(
                label,
                df_str,
                ds_id,
                redis_host,
                redis_port,
                redis_db,
                redis_key,
                e))
        return ae_consts.ERR, None
    # end of try/ex extract from redis

    log.debug(
        '{} - {} ds_id={} extract scrub={}'.format(
            label,
            df_str,
            ds_id,
            scrub_mode))

    scrubbed_df = scrub_utils.extract_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=df_type,
        msg_format='df={} date_str={}',
        ds_id=ds_id,
        df=df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of extract_yahoo_news_dataset


def extract_option_calls_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_option_calls_dataset

    Extract the Yahoo options calls for a ticker and
    return it as a ``pandas.Dataframe``

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    label = '{}-calls'.format(work_dict.get('label', 'extract'))
    ds_id = work_dict.get('ticker')
    df_type = yahoo_consts.DATAFEED_OPTIONS_YAHOO
    df_str = yahoo_consts.get_datafeed_str_yahoo(df_type=df_type)
    redis_key = work_dict.get(
        'redis_key',
        work_dict.get('calls', 'missing-redis-key'))
    s3_key = work_dict.get(
        's3_key',
        work_dict.get('calls', 'missing-s3-key'))
    redis_host = work_dict.get(
        'redis_host',
        None)
    redis_port = work_dict.get(
        'redis_port',
        None)
    redis_db = work_dict.get(
        'redis_db',
        ae_consts.REDIS_DB)

    log.debug(
        '{} - {} - start - redis_key={} s3_key={}'.format(
            label,
            df_str,
            redis_key,
            s3_key))

    if not redis_host and not redis_port:
        redis_host = ae_consts.REDIS_ADDRESS.split(':')[0]
        redis_port = ae_consts.REDIS_ADDRESS.split(':')[1]

    exp_date_str = None
    calls_df = None
    status = ae_consts.NOT_RUN
    try:
        redis_rec = redis_get.get_data_from_redis_key(
            label=label,
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=work_dict.get('password', None),
            key=redis_key,
            decompress_df=True)

        status = redis_rec['status']
        log.debug(
            '{} - {} redis get data key={} status={}'.format(
                label,
                df_str,
                redis_key,
                ae_consts.get_status(status=status)))

        if status == ae_consts.SUCCESS:
            calls_json = None
            if 'calls' in redis_rec['rec']['data']:
                calls_json = redis_rec['rec']['data']['calls']
            else:
                calls_json = redis_rec['rec']['data']
            log.debug(
                '{} - {} redis convert calls to df'.format(
                    label,
                    df_str))
            exp_date_str = None
            try:
                calls_df = pd.read_json(
                    calls_json,
                    orient='records')
                exp_epoch_value = calls_df['expiration'].iloc[-1]
                exp_date_str = ae_utils.convert_epoch_to_datetime_string(
                    epoch=exp_epoch_value,
                    fmt=ae_consts.COMMON_DATE_FORMAT,
                    use_utc=True)
            except Exception as f:
                log.debug(
                    '{} - {} redis_key={} '
                    'no calls df found'.format(
                        label,
                        df_str,
                        redis_key))
                return ae_consts.EMPTY, None
            # end of try/ex to convert to df
            log.debug(
                '{} - {} redis_key={} calls={} exp_date={}'.format(
                    label,
                    df_str,
                    redis_key,
                    len(calls_df.index),
                    exp_date_str))
        else:
            log.debug(
                '{} - {} did not find valid redis option calls '
                'in redis_key={} status={}'.format(
                    label,
                    df_str,
                    redis_key,
                    ae_consts.get_status(status=status)))

    except Exception as e:
        log.debug(
            '{} - {} - ds_id={} failed getting option calls from '
            'redis={}:{}@{} key={} ex={}'.format(
                label,
                df_str,
                ds_id,
                redis_host,
                redis_port,
                redis_db,
                redis_key,
                e))
        return ae_consts.ERR, None
    # end of try/ex extract from redis

    log.debug(
        '{} - {} ds_id={} extract scrub={}'.format(
            label,
            df_str,
            ds_id,
            scrub_mode))

    scrubbed_df = scrub_utils.extract_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=df_type,
        msg_format='df={} date_str={}',
        ds_id=ds_id,
        df=calls_df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of extract_option_calls_dataset


def extract_option_puts_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_option_puts_dataset

    Extract the Yahoo options puts for a ticker and
    return it as a ``pandas.Dataframe``

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    label = '{}-puts'.format(work_dict.get('label', 'extract'))
    ds_id = work_dict.get('ticker')
    df_type = yahoo_consts.DATAFEED_OPTIONS_YAHOO
    df_str = yahoo_consts.get_datafeed_str_yahoo(df_type=df_type)
    redis_key = work_dict.get(
        'redis_key',
        work_dict.get('puts', 'missing-redis-key'))
    s3_key = work_dict.get(
        's3_key',
        work_dict.get('puts', 'missing-s3-key'))
    redis_host = work_dict.get(
        'redis_host',
        None)
    redis_port = work_dict.get(
        'redis_port',
        None)
    redis_db = work_dict.get(
        'redis_db',
        ae_consts.REDIS_DB)

    log.debug(
        '{} - {} - start - redis_key={} s3_key={}'.format(
            label,
            df_str,
            redis_key,
            s3_key))

    if not redis_host and not redis_port:
        redis_host = ae_consts.REDIS_ADDRESS.split(':')[0]
        redis_port = ae_consts.REDIS_ADDRESS.split(':')[1]

    exp_date_str = None
    puts_df = None
    status = ae_consts.NOT_RUN
    try:
        redis_rec = redis_get.get_data_from_redis_key(
            label=label,
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=work_dict.get('password', None),
            key=redis_key,
            decompress_df=True)

        status = redis_rec['status']
        log.debug(
            '{} - {} redis get data key={} status={}'.format(
                label,
                df_str,
                redis_key,
                ae_consts.get_status(status=status)))

        if status == ae_consts.SUCCESS:
            puts_json = None
            if 'puts' in redis_rec['rec']['data']:
                puts_json = redis_rec['rec']['data']['puts']
            else:
                puts_json = redis_rec['rec']['data']
            log.debug(
                '{} - {} redis convert puts to df'.format(
                    label,
                    df_str))
            try:
                puts_df = pd.read_json(
                    puts_json,
                    orient='records')
                exp_epoch_value = puts_df['expiration'].iloc[-1]
                exp_date_str = ae_utils.convert_epoch_to_datetime_string(
                    epoch=exp_epoch_value,
                    fmt=ae_consts.COMMON_DATE_FORMAT,
                    use_utc=True)
            except Exception as f:
                log.debug(
                    '{} - {} redis_key={} '
                    'no puts df found'.format(
                        label,
                        df_str,
                        redis_key))
                return ae_consts.EMPTY, None
            # end of try/ex to convert to df
            log.debug(
                '{} - {} redis_key={} puts={} exp_date={}'.format(
                    label,
                    df_str,
                    redis_key,
                    len(puts_df.index),
                    exp_date_str))
        else:
            log.debug(
                '{} - {} did not find valid redis option puts '
                'in redis_key={} status={}'.format(
                    label,
                    df_str,
                    redis_key,
                    ae_consts.get_status(status=status)))

    except Exception as e:
        log.debug(
            '{} - {} - ds_id={} failed getting option puts from '
            'redis={}:{}@{} key={} ex={}'.format(
                label,
                df_str,
                ds_id,
                redis_host,
                redis_port,
                redis_db,
                redis_key,
                e))
        return ae_consts.ERR, None
    # end of try/ex extract from redis

    log.debug(
        '{} - {} ds_id={} extract scrub={}'.format(
            label,
            df_str,
            ds_id,
            scrub_mode))

    scrubbed_df = scrub_utils.extract_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=df_type,
        msg_format='df={} date_str={}',
        ds_id=ds_id,
        df=puts_df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of extract_option_puts_dataset
