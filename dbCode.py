from flask import Flask, render_template, request, redirect, url_for
import pymysql
import creds
import boto3

def get_conn():
    # To connect MySQL database
    return pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.password,
        db=creds.db,
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(query, args=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()
  
# Driver Code
if __name__ == "__main__" :
    mysqlconnect()