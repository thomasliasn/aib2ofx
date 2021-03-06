#!/usr/bin/env python
# coding: utf-8

from BeautifulSoup import BeautifulStoneSoup
import re, os, subprocess, fnmatch, codecs 
from datetime import datetime

class PdfParse:
    def __init__(self, directory):
        self.debit_rpos=307
        self.credit_rpos=363
        self.balance_rpos=430
        self.desc_lpos=79

        self.dateRegEx = '\d+\s\w+\s\d{4,4}' 
        self.accountNoRegEx = '\d{5,5}-\d{3,3}'
        self.directory = os.path.abspath(directory)

    def getData(self):
        files = os.listdir(self.directory)		
        data=[]
        for f in files:
            if fnmatch.fnmatch(f, '*.pdf'):
                fullname = self.directory+"/"+f
                subprocess.call(['pdftohtml', '-xml', fullname])
                fullname = fullname.rstrip('.pdf')+".xml"	
                data.append(self._get_data_for_file(fullname))
        return data

    def _get_data_for_file(self, file_name):
        data =  {'type':'checking',
                'available': '',
                'balance' : '',
                'bankId': 'AIB',
                'currency': 'EUR',
                'operations': []}

        statement = self._parse_xml(file_name)
        data['accountId']=statement['accountId'] 

        operations = statement['operations']
        data['operations']=operations
        data['balance']=operations[-1]['balance']
        data['available']=data['balance']
        data['reportDate']=operations[-1]['timestamp']
        return data

    def _parse_xml(self, file_name):
        file = codecs.open(file_name, "r")
        xml = file.read()
        soup = BeautifulStoneSoup(xml);

        operations=[]
        current_ts = ''
        accountId = ''
        #Template for an operation
        operation_tmpl = dict(debit='',credit='',balance='',description='')
        operation=operation_tmpl.copy()

        for elm in soup.findAll('text'):
            right_pos=int(elm['left'])+int(elm['width'])
            left_pos=int(elm['left'])

            accountIdMatch = re.search(self.accountNoRegEx, elm.text)
            if(accountIdMatch):
                accountId=accountIdMatch.group(0) 

            if(left_pos<=70):
                dateMatch = re.search(self.dateRegEx,elm.text)
                if(dateMatch):
                    date = dateMatch.group(0)
                    operation['description'] = elm.text.replace(date,'').lstrip()
                    current_ts = datetime.strptime(date, '%d %b %Y')
            if(right_pos==self.debit_rpos):
                operation['debit'] = elm.text
                operations.append(operation)
                operation=operation_tmpl.copy()
            if(right_pos==self.credit_rpos):
                operation['credit'] = elm.text
                operations.append(operation)
                operation=operation_tmpl.copy()
            if(left_pos==self.desc_lpos):
                operation['description'] = elm.text

            if(right_pos==self.balance_rpos and len(operations)):
                operations[-1]['balance'] = elm.text

            operation['timestamp'] = current_ts 

        return {'accountId':accountId, 'operations':operations}
