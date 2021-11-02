from flask import flash

from db.db_insert import update_on_dupkey, query_keyword_id, query_campaign_id, query_adgroup_id, \
    update_on_dupkey_negative, update_on_dupkey_search, query_search_id, query_negative_id
from models.keywordmodel import Keyword, typeEnum
import datetime

from models.negativemodel import NegativeKeyword
from models.searchmodel import SearchKeyTerm


def parse_xlsx(df1):
    if 'Keyword' in df1.columns:
        parse_keyword(df1)
    elif 'Negative keyword' in df1.columns:
        parse_negative_keyword(df1)
    elif 'Search term' in df1.columns:
        parse_search_term(df1)
    else:
        flash('Incorrect file format')


def parse_keyword(df1):
    df1 = df1.astype({"Keyword status": str, "Keyword": str, "Campaign": str, "Ad group": str})
    for i, row in df1.iterrows():
        if row['Keyword'].startswith('"'):
            match_type = typeEnum.phrase
            keyword = row['Keyword'][1:-1]
        elif row['Keyword'].startswith('['):
            match_type = typeEnum.exact
            keyword = row['Keyword'][1:-1]
        else:
            match_type = typeEnum.broad
            keyword = row['Keyword']

        if row['Keyword status'] == "Enabled":
            is_active = True
        else:
            is_active = False

        keyword_id = query_keyword_id(keyword)
        if keyword_id is None:
            update_on_dupkey(Keyword, {'word': keyword, 'type': match_type,
                                       'is_active': is_active, 'created_time': datetime.datetime.now()})
        else:
            update_on_dupkey(Keyword, {'id': keyword_id[0], 'type': match_type,
                                       'is_active': is_active, 'created_time': datetime.datetime.now()})
        keyword_id = query_keyword_id(keyword)
        adgroup_id = query_adgroup_id(row['Ad group'])
        search_id = query_search_id(keyword_id[0])
        if search_id is None:
            update_on_dupkey(SearchKeyTerm, {'keyword_id': keyword_id, 'ad_group_id': adgroup_id[0],
                                             'created_time': datetime.datetime.now()})
        else:
            update_on_dupkey(SearchKeyTerm, {'id': search_id, 'ad_group_id': adgroup_id,
                                             'created_time': datetime.datetime.now()})


def parse_negative_keyword(df1):
    df1 = df1.astype({"Negative keyword": str, "Campaign": str, "Ad group": str, "Match type": str})
    for i, row in df1.iterrows():
        if 'broad' in row['Match type'].lower():
            match_type = typeEnum.broad
        elif 'exact' in row['Match type'].lower():
            match_type = typeEnum.exact
        elif 'phrase' in row['Match type'].lower():
            match_type = typeEnum.phrase
        else:
            match_type = None

        keyword_id = query_keyword_id(row['Negative keyword'])
        if keyword_id is None:
            update_on_dupkey(Keyword, {'word': row['Negative keyword'], 'type': match_type,
                                       'created_time': datetime.datetime.now()})
        else:
            update_on_dupkey(Keyword, {'id': keyword_id[0], 'word': row['Negative keyword'],
                                       'type': match_type, 'created_time': datetime.datetime.now()})
        keyword_id = query_keyword_id(row['Negative keyword'])
        campaign_id = query_campaign_id(row['Campaign'])
        ad_group_id = query_adgroup_id(row['Ad group'])
        if campaign_id is not None:
            campaign_id = campaign_id[0]
        if ad_group_id is not None:
            ad_group_id = ad_group_id[0]
        negative_id = query_negative_id(campaign_id, ad_group_id, keyword_id[0])
        if negative_id is None:
            update_on_dupkey_negative(NegativeKeyword, {'campaign_id': campaign_id, 'ad_group_id': ad_group_id,
                                                        'keyword_id': keyword_id[0]})
        else:
            update_on_dupkey_negative(NegativeKeyword, {'id': negative_id[0], 'campaign_id': campaign_id,
                                                        'ad_group_id': ad_group_id, 'keyword_id': keyword_id[0]})


def parse_search_term(df1):
    df1 = df1.astype({"Search term": str, "Match type": str, "Added/Excluded": str, "Ad group": str})
    for i, row in df1.iterrows():
        if 'broad' in row['Match type'].lower():
            match_type = typeEnum.broad
        elif 'exact' in row['Match type'].lower():
            match_type = typeEnum.exact
        elif 'phase' in row['Match type'].lower():
            match_type = typeEnum.phrase
        else:
            match_type = None

        if row["Added/Excluded"] == "Added":
            is_added = True
        else:
            id_added = False

        update_on_dupkey(Keyword, {'word': row['Search term'], 'type': match_type,
                                   'is_active': is_added, 'created_time': datetime.datetime.now()})
        term_id = query_keyword_id(row['Search term'])
        adgroup_id = query_adgroup_id(row['Ad group'])
        update_on_dupkey_search(SearchKeyTerm, {'keyword_id': term_id, 'ad_group_id': adgroup_id,
                                                'created_time': datetime.datetime.now()})

