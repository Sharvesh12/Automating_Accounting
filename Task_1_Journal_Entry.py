#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 23:59:30 2019

@author: sharvesh
"""
#Imports:
import pandas as pd
import numpy as np


#Reading input files into dataframes:
invoice_data = pd.read_csv("Billie/input/A1_invoice_data_extract.csv")
chart_accounts = pd.read_csv("Billie/input/A2_chart_of_accounts.csv")
bank_data = pd.read_csv("Billie/input/A3_bank_data_extract.csv")
journal_entry_temp = pd.read_csv("Billie/input/A4_journal_entry_import_template.csv")

#Data Cleaning: Removing 'nan' records
invoice_data = invoice_data.dropna(axis=0, how='all')


# Creating empty Dataframes with column names only
JE1 =  pd.DataFrame(columns=[        'JOURNAL_ENTRY_ID', 
                                     'ENTITY_ID', 
                                     'TRAN_DATE',
                                     'ACCOUNT',
                                     'DEBIT',
                                     'CREDIT',
                                     'MEMO'])

#Fetching credit and debit amounts respectively from bank_data:

JE1['CREDIT'] = invoice_data['INVOICE_AMOUNT']
JE1['DEBIT'] = invoice_data['PAYOUT_AMOUNT'] + invoice_data['FEE_AMOUNT']

#Auto-incrementation of 'JOURNAL_ENTRY_ID' as unique identifiers:

s = "JNL-EXAMPLE-"
i = 1
for j in (JE1.index):
    comp = s+str(i)
    i = i+1
    JE1.iloc[(i-2),0] = comp
 
JE1['ENTITY_ID'] = "2d15c94c-595c-4c60-a41f-594d5c0e6618"

#TRAN_DATE:


#Fetching COMPLETED_DATE and PAYOUT_DATE from 'invoice_data':
JE1 = JE1.merge(invoice_data[['COMPLETED_DATE', 'INVOICE_AMOUNT']],left_on = 'CREDIT', right_on = 'INVOICE_AMOUNT', how='left')
JE1 = JE1.drop(columns = ['INVOICE_AMOUNT'])
JE1 = JE1.merge(invoice_data[['PAYOUT_DATE', 'PAYOUT_AMOUNT']],left_on = 'DEBIT', right_on = 'PAYOUT_AMOUNT', how='left')
JE1 = JE1.drop(columns = ['PAYOUT_AMOUNT'])
JE1= JE1.drop_duplicates(subset= 'JOURNAL_ENTRY_ID', inplace=False)


#Consolidating COMPLETED_DATE and PAYOUT_DATE within TRAN_DATE:
JE1.loc[JE1['COMPLETED_DATE'].isnull(), 'TRAN_DATE'] = JE1['PAYOUT_DATE']
JE1.loc[JE1['PAYOUT_DATE'].isnull(), 'TRAN_DATE'] = JE1['COMPLETED_DATE']
JE1 = JE1.drop(['COMPLETED_DATE','PAYOUT_DATE'], axis=1)

#Filtering 'factoring transactions' from october only:
import datetime 
JE1['TRAN_DATE'] = pd.to_datetime(JE1['TRAN_DATE'], format='%Y-%m-%d') #conversion from string to date object

JE1 = JE1[  (JE1['TRAN_DATE'] >= '2019-10-01') & (JE1['TRAN_DATE'] <= '2019-10-31')   ] 


#MEMO:

#Fetching INVOICE_ID and CUSTOMER_ID from 'invoice_data':
JE1 = JE1.merge(invoice_data[['INVOICE_ID', 'CUSTOMER_ID', 'INVOICE_AMOUNT']],left_on = 'CREDIT', right_on = 'INVOICE_AMOUNT' , how='left')
JE1 = JE1.drop_duplicates(subset= 'JOURNAL_ENTRY_ID', inplace=False)
JE1 = JE1.drop(columns = ['INVOICE_AMOUNT'])
JE1 = JE1.merge(invoice_data[['INVOICE_ID', 'CUSTOMER_ID', 'PAYOUT_AMOUNT']],left_on = 'DEBIT', right_on = 'PAYOUT_AMOUNT' , how='left')
JE1 = JE1.drop_duplicates(subset= 'JOURNAL_ENTRY_ID', inplace=False)
JE1 = JE1.drop(columns = ['PAYOUT_AMOUNT'])


#Consolidation of INVOICE_ID and CUSTOMER_ID:
JE1.loc[JE1['INVOICE_ID_x'].isnull(), 'INVOICE_ID_x'] = JE1['INVOICE_ID_y']
JE1.loc[JE1['CUSTOMER_ID_x'].isnull(), 'CUSTOMER_ID_x'] = JE1['CUSTOMER_ID_y']
JE1 = JE1.drop(['INVOICE_ID_y','CUSTOMER_ID_y'], axis=1)
JE1 = JE1.reset_index(drop = True)


#Formatting memo in the string format required using Supplier Invoice ID and Supplier ID:
if(len(JE1.INVOICE_ID_x) >0):
    JE1.MEMO =  "Supplier invoice for " + JE1.INVOICE_ID_x + " and Supplier " + JE1.CUSTOMER_ID_x 
    
JE1 = JE1.drop(['INVOICE_ID_x','CUSTOMER_ID_x'], axis=1)

#Massaging the dataframe into identifier variables and measured variables

melted = pd.melt(JE1, id_vars=['JOURNAL_ENTRY_ID','ENTITY_ID','TRAN_DATE','ACCOUNT','MEMO'], value_vars=['DEBIT', 'CREDIT'])


melted.loc[melted['variable'] == 'DEBIT', 'DEBIT'] = melted['value']
melted.loc[melted['variable'] == 'CREDIT', 'CREDIT'] = melted['value']

melted = melted.drop(['variable','value'], axis=1)

melted.index = melted['JOURNAL_ENTRY_ID']

#Journal entry id genreation for accounts

melted['indexNumber'] = melted.index.str.rsplit('-').str[-1].astype(int)
melted = melted.sort_values(['indexNumber']).drop('indexNumber', axis=1)

melted = melted.reset_index(drop = True) 

#ACCOUNT NO: Random selection of account numbers from 'chart_accounts' based on assumption
#Additional Information : Account numbers associated with invoice data would be helpful 
#                         to combine account numbers to Journal Entries

acc = list(chart_accounts['Account No.'])
melted['ACCOUNT'] = np.random.choice(acc, len(melted))

cols = list(melted.columns.values)
melted = melted[['JOURNAL_ENTRY_ID', 'ENTITY_ID', 'TRAN_DATE', 'ACCOUNT', 'DEBIT','CREDIT','MEMO']]