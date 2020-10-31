# coding: utf-8

from xlrd import open_workbook
import re
import types

class XlsReader(object):
    # 创建一个用于读取sheet的生成器,依次生成每行数据,row_count 用于指定读取多少行, col_count 指定用于读取多少列
    def readsheet(self,s, row_count=-1, col_count=-1):  #
        # Sheet 有多少行
        nrows = s.nrows
        # Sheet 有多少列
        ncols = s.ncols
        row_count = (row_count if row_count > 0 else nrows)
        col_count = (col_count if col_count > 0 else ncols)
        row_index = 0
        while row_index < row_count:
            yield [s.cell(row_index, col).value for col in range(col_count)]
            row_index += 1

    def readHosts(self,local_file,row_count=-1, col_count=-1):
        hosts = []
        wb = open_workbook(local_file)  # 打开Excel文件
        # 读取Excel中所有的Sheet
        for s in wb.sheets():
            for row in self.readsheet(s, 0, 0):
                # if type(row[3]) is types.FloatType:
                #       row[3] = int(row[3])
                hosts.append(row[0]+" "+row[1]+" "+row[2]+" "+str(row[3]))
        return hosts