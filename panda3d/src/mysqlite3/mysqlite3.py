#
#
# Class for sqlite3
#     
#import sys
import sqlite3
import traceback
#import pandas
#import os
#from math import sqrt
#import json
#import time
#from datetime import datetime
#
# Private API Class for sqlite3
#
class MyDb:
    def __init__(self, dbpath='../Auto-trade.db'):
        self.dbpath = dbpath
        self.conn = sqlite3.connect(dbpath)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
    #
    def rollback(self):
        self.conn.rollback()
    #
    def commit(self):
        self.conn.commit()
    #
    # execute select statement
    #
    def query(self, sql):
        try:
            rs = self.cur.execute(sql)
        except:
            print(f"{traceback.format_exc()}")
            print(f"sql:{sql}")
        return rs
    #
    # fetch next record
    #
    def fetch_next(self):
        try:
            rs = self.cur.fetchone()
        except:
            rs = None
            print(f"{traceback.format_exc()}")
        return rs
    #
    # execute insert/update statement
    #
    def execute(self, sql):
        try:
            self.cur.execute(sql)
        except:
            print(f"{traceback.format_exc()}")
            print(f"sql:{sql}")
        return
    #
    # close database
    #
    def close(self):
        self.conn.close()
        self.conn = None
    #
    # re-connect database
    #
    def reopen(self):
        if self.conn != None:
            self.conn.close()
        self.conn = sqlite3.connect(self.dbpath)
    #
    # entry cube's pattern to pattern-table
    #
    def insert_pattern(self, pt_id, cube1, cube2, cube3):
        sql = "select pt_id from pattern where "\
            + f"pos1='{cube1[0]}' and col1='{cube1[1]}' and "\
            + f"pos2='{cube2[0]}' and col2='{cube2[1]}' and "\
            + f"pos3='{cube3[0]}' and col3='{cube3[1]}'"
        rs = self.query(sql).fetchone()
        if rs == None:
            sql = "insert into pattern(pt_id,pos1,col1,pos2,col2,pos3,col3) values("\
                + f"'{pt_id}',"\
                + f"'{cube1[0]}',"\
                + f"'{cube1[1]}',"\
                + f"'{cube2[0]}',"\
                + f"'{cube2[1]}',"\
                + f"'{cube3[0]}',"\
                + f"'{cube3[1]}')"
            self.execute(sql)
        else:
            pt_id = rs['pt_id']
        return pt_id
    #
    # entry cube's completed pattern to com_pattern-table
    #
    def insert_comp(self, cube1, cube2, cube3, pitch, roll):
        entry_no = None
        sql = "select entry_no from comp_pattern where "\
            + f"pos1='{cube1[0]}' and col1='{cube1[1]}' and "\
            + f"pos2='{cube2[0]}' and col2='{cube2[1]}' and "\
            + f"pos3='{cube3[0]}' and col3='{cube3[1]}'"
        rs = self.query(sql).fetchone()
        if rs == None:
            entry_no = 0
            sql = "insert into comp_pattern(pos1,col1,pos2,col2,pos3,col3,pitch,roll) values("\
                + f"'{cube1[0]}',"\
                + f"'{cube1[1]}',"\
                + f"'{cube2[0]}',"\
                + f"'{cube2[1]}',"\
                + f"'{cube3[0]}',"\
                + f"'{cube3[1]}',"\
                + f"{pitch},{roll})"
            self.execute(sql)
        else:
            entry_no = rs['entry_no']
        return entry_no
    #
    # search comp_pattern-table by current cube's attr.
    #
    def search_comp(self, cube1, cube2, cube3):
        sql = "select entry_no from comp_pattern where "\
            + f"pos1='{cube1[0]}' and col1='{cube1[1]}' and "\
            + f"pos2='{cube2[0]}' and col2='{cube2[1]}' and "\
            + f"pos3='{cube3[0]}' and col3='{cube3[1]}'"
        #print(f"sql:{sql}")
        rs = self.query(sql).fetchone()
        if rs == None:
            entry_no = None
        else:
            entry_no = rs['entry_no']
        return entry_no
    #
    # entry solution to solution-table
    #
    def insert_solution(self, pt_id, cmd):
        sql = "select pt_id, sl_no, sl_st, cmd from solution where "\
            + f"pt_id='{pt_id}' ORDER BY sl_no DESC LIMIT 1"
        rs = self.query(sql).fetchone()
        if rs == None:
            # insert new pt_id with sl_no=0
            sl_no = 0
            sql = "insert into solution(pt_id,sl_no,cmd) values("\
                + f"'{pt_id}',"\
                + f"{sl_no},"\
                + f"'{cmd}')"
            self.execute(sql)
        else:
            sl_no = rs['sl_no']
            if rs['sl_st'] == 1:
                # insert new record with incremental ls_no
                sl_no += 1
                sql = "insert into solution(pt_id,sl_no,cmd) values("\
                    + f"'{pt_id}',"\
                    + f"{sl_no},"\
                    + f"'{cmd}')"
                self.execute(sql)
            else:
                # update 'cmd' 
                cmd = rs['cmd'] + cmd
                sql = f"update solution set cmd='{cmd}'"\
                    + f" where pt_id='{pt_id}' and sl_no={sl_no}"
                self.execute(sql)
        return sl_no
    #
    # update 'sl_st' to 1 and commit 'insert'/'update' statement
    #  
    def commit_solution(self, pt_ids):
        for pt_id in pt_ids:
            sql = f"update solution set sl_st=1"\
                + f" where pt_id='{pt_id}'"
            self.execute(sql)
        self.conn.commit()
        return
    #
    # search pattern-table by current cube's attr.
    #
    def search_pattern(self, cube1, cube2, cube3):
        sql = "select pt_id from pattern where "\
            + f"pos1='{cube1[0]}' and col1='{cube1[1]}' and "\
            + f"pos2='{cube2[0]}' and col2='{cube2[1]}' and "\
            + f"pos3='{cube3[0]}' and col3='{cube3[1]}'"
        #print(f"sql:{sql}")
        rs = self.query(sql).fetchone()
        if rs == None:
            pt_id = None
        else:
            pt_id = rs['pt_id']
        return pt_id
    #
    # get pattern by pt_id.
    #
    def get_pattern(self, pt_id):
        sql = "select pt_id,pos1,col1,pos2,col2,pos3,col3 from pattern where "\
            + f"pt_id LIKE '%{pt_id}%' ORDER BY inserted_at ASC"
        rs = self.query(sql).fetchone()
        if rs == None:
            pt_id = None
            cube1 = None
            cube2 = None
            cube3 = None
        else:
            pt_id = rs['pt_id']
            cube1 = (rs['pos1'],rs['col1'])
            cube2 = (rs['pos2'],rs['col2'])
            cube3 = (rs['pos3'],rs['col3'])
        return pt_id,cube1,cube2,cube3
    #
    # get next pattern.
    #
    def next_pattern(self):
        rs = self.fetch_next()
        if rs == None:
            pt_id = None
            cube1 = None
            cube2 = None
            cube3 = None
        else:
            pt_id = rs['pt_id']
            cube1 = (rs['pos1'],rs['col1'])
            cube2 = (rs['pos2'],rs['col2'])
            cube3 = (rs['pos3'],rs['col3'])
        return pt_id,cube1,cube2,cube3
    #
    # get solution(sl_no=Max) by pt_id.
    #
    def get_solution(self, pt_id):
        sql = "select sl_no, cmd from solution where "\
            + f"pt_id='{pt_id}' and sl_st=1 ORDER BY sl_no DESC LIMIT 1"
        rs = self.query(sql).fetchone()
        if rs == None:
            cmd = None
            sl_no = None
        else:
            cmd = rs['cmd']
            sl_no = rs['sl_no']
        return cmd,sl_no

    #
    # delete records from table('pattern'/'solution').
    #
    def delete_pattern(self, match = None):
        tables = ('pattern', 'solution')
        if match != None:
            strWhere = f" where pt_id LIKE '%{match}%'"
        else:
            strWhere = ''
        #
        for table in tables:
            sql = f"delete from {table}"
            self.execute(sql + strWhere)
        #
        self.conn.commit()
        return
    #
#
#eof
