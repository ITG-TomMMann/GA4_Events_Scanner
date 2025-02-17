
# """
# PART 2

# IMPORTING OUTPUT FROM BIGQUERY WITH PAGE_PATH AND METRICS AFTER BEING ON THAT PAGE
# MATCHING TO THE CRAWLED LINKS ABOVE
# FILTERING
# LOOKING AT DISTRUBUTIONS OF METRICS

# @author: martinconnor
# """

# # pip install requests beautifulsoup4 pandas nltk spacy
# # pip install requests beautifulsoup4 selenium webdriver_manager
# # python -m spacy download en_core_web_sm

# # import pandas as pd
# import os
# # import numpy as np
# # from datetime import datetime, timedelta

# import matplotlib.pyplot as plt
# import seaborn as sns
# # from scipy.stats import shapiro, normaltest, anderson
# # import statsmodels.api as sm

# #WORKING DIRECTORY
# os.chdir(r'<C:\WHEREVER YOUR BQ DATA IS SAVED TO>\Data')



# # READ IN THE CSV FILE
# df_page_paths01 = pd.read_csv(BQ_filename, parse_dates=True)
# df_page_paths01.columns = [col if 'SessionsCount' in col else col.lower() for col in df_page_paths01.columns]

# # Filter to remove:
#     # the Totals Rows
#     # NULL page_path
#     # Rows >= 500 sessions OR found in the df_links from the crawl in previous prog
    
#     # Keep:
#     # GB
#     # landrover.co.uk


# # CREATE AS A FILTER COLUMN CALLED KEEP



# # lst_crawled_urls = [link.replace('https://','').lower() for link in df_links['URL'].tolist()]
# lst_crawled_urls = [link.replace('https://','').lower() for country, link in df_links_dict['URL'].tolist()]

# # Dictionary to store lists of found URLs
# found_urls = {}

# for country, df in df_links_dict.items():
#     # Assuming the crawled URLs are stored in a column named "found_urls" in each DataFrame
#     found_urls[country] = df["URL"].tolist()  # Convert column to list

# # Now, found_urls["GB"], found_urls["DE"], etc. contain lists of URLs found in each country's DataFrame.
# lst_crawled_urls = [url.replace('https://','').lower() for urls in found_urls.values() for url in urls]





# df_page_paths01['keep'] = df_page_paths01.apply(lambda x: 1 if x['page_path'] in(lst_crawled_urls ) and x['SessionsCount'] >= 100
#                                                 else 0 if x['page_path'] in(['Totals','nan',''])
#                                                 else 0 if x['SessionsCount'] <= 500
#                                                 else 0 if x['market_code'] not in(lst_markets)
#                                                 else 1
#                                                 ,axis=1)
# df_page_paths01['page_path_check'] = df_page_paths01.apply(lambda x: 1 if str(x['page_path']) in(lst_crawled_urls )
#                                                 else 0
#                                                 ,axis=1)

# # count of the matched paths and filters
# df_page_paths01.groupby(['keep','page_path_check'])['page_path'].count() 

        
# df_page_paths01_filt = df_page_paths01.loc[df_page_paths01['keep']==1]



# # CHECK DATA TYPES
# df_page_paths01_filt.dtypes


# # VISUALIZE DISTRIBUTIONS OF THE METRICS

# def plot_distributions(df, metrics, market_code_col):
#     unique_market_codes = df[market_code_col].unique()
    
#     for market_code in unique_market_codes:
#         print(f"Market Code: {market_code}")
#         df_market = df[df[market_code_col] == market_code]
        
#         for metric in metrics:
#             plt.figure(figsize=(12, 6))
            
#             # Histogram
#             plt.subplot(1, 2, 1)
#             sns.histplot(df_market[metric], kde=True)
#             plt.title(f'Histogram of {metric} in {market_code}')
            
#             # Q-Q Plot
#             # plt.subplot(1, 2, 2)
#             # sm.qqplot(df_market[metric], line ='45')
#             # plt.title(f'Q-Q Plot of {metric} in {market_code}')
            
#             plt.show()


# # WHICH COLS TO USE?
# df_page_paths01_filt.columns

# metrics = [
#     # 'AVG_SessionSecondsAfterContent',
#         # 'sessions_Exited_At_Content',
#         # 'sessions_enquiry_flag',
#         # 'sessions_engagement_flag',
#         # 'sessions_ViewedNameplateContentPage',
#         # 'sessions_Conversion',
#         # 'sessions_ConfigurationStart',
#         # 'sessions_ConfigurationComplete',       
#         # 'sessions_Bounced_Session',
#         # 'AVG_PagesViewedAfterContent', 
#         # 'STDDEV_PagesViewedAfterContent',
#         # 'sessions_returning_visitor',
#         # 'AVG_time_on_site_seconds',
#         # 'STDDEV_time_on_site_seconds',
#         'SessionsCount',
#         # 'SessionsCountCheck',
#         # 'EnquiryRate',
#         # 'EngagementRate',
#         # 'ConversionRate',
#         # 'ConfigurationStartRate',
#         # 'ConfigurationCompleteRate',
#         # 'BounceRate',
#         # 'ExitRate'
#        ]
# plot_distributions(df_page_paths01_filt, metrics, 'market_code')


# # # Normal Distribution Test
# # def test_normality(df, metrics, market_code_col):
# #     unique_market_codes = df[market_code_col].unique()
# #     results = []

# #     for market_code in unique_market_codes:
# #         df_market = df[df[market_code_col] == market_code]
        
# #         for metric in metrics:
# #             # Shapiro-Wilk Test
# #             stat, p_value = shapiro(df_market[metric])
# #             result = {
# #                 'market_code': market_code,
# #                 'metric': metric,
# #                 'Shapiro-Wilk p-value': p_value,
# #                 'is_normal': p_value > 0.05  # Typically, p > 0.05 indicates normality
# #             }
# #             results.append(result)
            
# #     results_df = pd.DataFrame(results)
# #     return results_df

# # df_normal_tests = test_normality(df_page_paths01_filt, metrics, 'market_code')


# # OUTPUT THE FILTERED TABLE TO EXCEL

# # File name
# filtered_filename = 'filtered_pages_MM_' + date_string + '.xlsx'
# df_page_paths01_filt.to_excel(filtered_filename, sheet_name = 'Filtered Table', index = False)
 
# # =============================================================================
# # SCREENSHOTS OF THE FILTERED URLs
# # =============================================================================
# #WORKING DIRECTORY
# os.chdir(r'<C:\WHEREVER YOU NEE TO SAVE OUTPUT>\Screenshots_MM')

# def capture_screenshot(driver, url, save_path):
#     driver.get(url)
#     time.sleep(5)  # Wait for the page to load
#     S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
#     driver.set_window_size(S('Width'), S('Height'))  # May need manual adjustment
#     driver.find_element(By.TAG_NAME, 'body').screenshot(save_path)

# def main():
#     driver = setup_driver()
#     # visited = set()
    
#     # links = set(df_links_dict[country]['URL'])
    
#     # Initialize a list to store the data
#     data = []
    
#     for i, link in enumerate(links):
#         try:
#             save_path = f'screenshot_{country}_{i+1}.png'
#             capture_screenshot(driver, link, save_path)
#             print(f'Screenshot saved to {save_path}')
            
#             # Append the URL and filename to the data list
#             data.append({'URL': link, 'Screenshot Filename': save_path})
#         except Exception as e:
#             print(f'Failed to capture screenshot for {link}: {e}')
#             data.append({'URL': link, 'Screenshot Filename': 'screenshot not returned'})
    
#     driver.quit()
    
#     # Create a DataFrame from the data list
#     df = pd.DataFrame(data)
#     csv_name = 'screenshots_deep_crawl' + country + '.csv' 
#     # Save the DataFrame to a CSV file
#     df.to_csv(csv_name , index=False)
#     print('DataFrame saved to screenshots.csv: ' + country)

# # USING ACROSS THE MULTIPLE MARKETS:
# for country in df_links_dict:   
#     srs_links = df_page_paths01_filt['page_path'].loc[df_page_paths01_filt['market_code']==country]
#     lst_links = ['https://' + item for item in srs_links]    
#     links = set(lst_links)
#     main()
