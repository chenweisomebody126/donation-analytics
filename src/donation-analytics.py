import math
import sys

class ContributionRecord():
    def __init__(self, cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id):
        self.cmts_id = cmts_id
        self.name = name
        self.zip_code = zip_code
        self.transaction_dt = transaction_dt
        self.transaction_amt = transaction_amt
        self.other_id = other_id
        self.year = None
        self.name_zip = None
        if not self.isRecordValid():
            raise ValueError('This record is not valid')

    '''
    ISRECORDVALID - check the record is valid including each field is valid or not. If valid,
    postprocess it if necessary.
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id
    Returns:
        boolean - is valid or not
    '''
    def isRecordValid(self):
        if self.isCmts_idValid()==False:
            return False
        if self.isNameValid() == False:
            return False
        if self.isZipValidRegulate() ==False:
            return False
        if self.isTransaction_dtValidGenerateYear() ==False:
            return False
        if self.isTransaction_amtValidConvert2Float() == False:
            return False
        if self.isOther_idValid() == False:
            return False
        self.name_zip = (self.name, self.zip_code)
        self.cmts_zip_year = (self.cmts_id, self.zip_code, self.year)
        return True
    '''
    isCmts_idValid - check the cmts_id is valid.
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id
    Returns:
        boolean - is valid or not
    '''
    def isCmts_idValid(self):
        if not self.cmts_id:
            return False
        return True
    '''
    isNameValid - check the name is valid.
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id
    Returns:
        boolean - is valid or not
    '''
    def isNameValid(self):
        if (not self.name) or (self.name.count(',')!= 1):
            return False
        for name_token in self.name.split(','):
            if not name_token:
                return False
            for char in name_token:
                if not char.isalpha() and not char.isspace():
                    return False
        return True
    '''
    isZipValidRegulate - check the zip_code is valid. If so,
    trancate to get the first five as zip code
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id
    Returns:
        boolean - is valid or not
    '''
    def isZipValidRegulate(self):
        if not self.zip_code or len(self.zip_code)< 5:
            return False
        if not self.zip_code.isdigit():
            return False
        self.zip_code =self.zip_code[:5]
        return True
    '''
    isTransaction_dtValidGenerateYear - check the transaction_dt is valid.
    If so, generate the year
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id
    Returns:
        boolean - is valid or not
    '''
    def isTransaction_dtValidGenerateYear(self):
        if not self.transaction_dt or len(self.transaction_dt) != 8:
            return False
        for digit in self.transaction_dt:
            if not digit.isdigit():
                return False
        self.year = self.transaction_dt[-4:]
        if not self.year.isdigit():
            return False
        if int(self.year)<2015:
            return False
        return True
    '''
    isTransaction_amtValidConvert2Float - check the transaction_amt is valid.
    If so, convert to float
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id
    Returns:
        boolean - is valid or not
    '''
    def isTransaction_amtValidConvert2Float(self):
        if not self.transaction_amt:
            return False
        try:
            self.transaction_amt = float(self.transaction_amt)
        except:
            return False
        return True
    '''
    isOther_idValid - check the other_id is valid.
    If so, convert to float
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id
    Returns:
        boolean - is valid or not
    '''
    def isOther_idValid(self):
        if self.other_id:
            return False
        return True

class DonorsStatus():
    def __init__(self, percent):
        self.percent = percent
        self.name_zip2year = {}
        self.cmts_zip_year2transaction_list = {}
        self.cmts_zip_year2cum_transaction = {}
    '''
    isLaterRepeatDonorElseCreateDonor - check the donator is repeat donator
    and also check it is a later record in terms of year
    in case that the records streaming in are out of order.
    If donator is the first time donator, create it.

    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id, name_zip, name_zip2year
    Returns:
        boolean - is valid or not
    '''
    def isLaterRepeatDonorElseCreateDonor(self, record):
        if record.name_zip not in self.name_zip2year:
            self.name_zip2year[record.name_zip] = record.year
            return False
        elif record.year < self.name_zip2year[record.name_zip]:
            return False
        else:
            return True
    '''
    updateContributionsFromRepeatDonorForRecipient - update the record transaction amount
    and save into cmts_zip_year2transaction_list, then calculate the cummulative amount
    save it in the cmts_zip_year2cum_transaction.
    Arguments:
        record - cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id, cmts_zip_year
    Returns:
        None
    '''
    def updateContributionsFromRepeatDonorForRecipient(self, record):
        cmts_zip_year = record.cmts_zip_year
        self.cmts_zip_year2transaction_list[cmts_zip_year] = self.cmts_zip_year2transaction_list.get(cmts_zip_year, []) + [record.transaction_amt]
        self.cmts_zip_year2cum_transaction[cmts_zip_year] = self.cmts_zip_year2cum_transaction.get(cmts_zip_year, 0.)+record.transaction_amt

'''
getPercent - read from percentile.txt to get percent
Arguments:
    percentTxt - percentile.txt
Returns:
    None
'''
def getPercent(percentTxt):
    with open(percentTxt, 'r') as percentFile:
        for line in percentFile:
            lineStriped = line.strip()
            if lineStriped.isdigit():
                return int(lineStriped)
'''
setContributionRecord - from each line of itcont.txt to create record
Arguments:
    inputLine - line of itcont.txt
Returns:
    record
'''
def setContributionRecord(inputLine):
    tokens = inputLine.split('|')
    cmts_id = tokens[0]
    name = tokens[7]
    zip_code = tokens[10]
    transaction_dt = tokens[13]
    transaction_amt = tokens[14]
    other_id = tokens[15]
    return ContributionRecord(cmts_id, name, zip_code, transaction_dt, transaction_amt, other_id)

'''
getOutputLine - from incoming record to get percentile, cum_transaction_amt, num_transaction
Arguments:
    donorsStatus - current status of recorded donors, in terms of transaction records
Returns:
    outputLine - a string of line containing cmts_id, zip_code, year, percentile, cum_transaction_amt, num_transaction
'''
def getOutputLine(donorsStatus, record):
    cmts_id = record.cmts_id
    zip_code = record.zip_code
    year = record.year
    cmts_zip_year = record.cmts_zip_year
    num_transaction = len(donorsStatus.cmts_zip_year2transaction_list[cmts_zip_year])
    percentile_idx = int(math.ceil(donorsStatus.percent * num_transaction/100.)-1)
    percentile = donorsStatus.cmts_zip_year2transaction_list[cmts_zip_year][percentile_idx]
    percentile = str(int(round(percentile)))
    cum_transaction_amt =donorsStatus.cmts_zip_year2cum_transaction[cmts_zip_year]
    cum_transaction_amt = str(int(round(cum_transaction_amt)))
    num_transaction = str(num_transaction)
    outputList = [cmts_id, zip_code, year, percentile, cum_transaction_amt, num_transaction]
    return '|'.join(outputList)

def main():

    try:
        contributionTxt = str(sys.argv[1])
        percentTxt = str(sys.argv[2])
        repeatDonorsTxt = str(sys.argv[3])
        print('?', contributionTxt, percentTxt,repeatDonorsTxt)
    except:
        print("The arguments have error")

    percent = getPercent(percentTxt)
    donorsStatus = DonorsStatus(percent)
    with open(contributionTxt, 'r') as inputFile:
        with open(repeatDonorsTxt, 'a') as outputFile:
            for inputLine in inputFile:
                try:
                    record = setContributionRecord(inputLine)
                except:
                    continue
                if donorsStatus.isLaterRepeatDonorElseCreateDonor(record):
                    donorsStatus.updateContributionsFromRepeatDonorForRecipient(record)
                    outputLine = getOutputLine(donorsStatus, record)
                    outputFile.write(outputLine+'\n')
    return


if __name__ == "__main__":
    main()
