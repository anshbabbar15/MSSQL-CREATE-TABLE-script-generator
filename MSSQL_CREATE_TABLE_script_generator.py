import pandas as pd
import math
import os

def get_column_name(col):
    col_name = col.strip()
    col_name = col_name.replace(' ', '_')
    col_name = col_name.replace('(', '').replace(')', '')
    col_name = col_name.replace('-', ' ')

    return col_name

def get_column_name_same(col):
    col_name = col.strip()  
    if ' ' in col_name or not col_name.isidentifier():
        col_name = f'[{col_name}]'
    return col_name

def determine_data_type(df, col_name):
    col_str = df[col_name].astype(str)
    
    if col_str.str.contains('%').any() or col_str.str.contains('₹').any():
        max_length = col_str.map(len).max()
        varchar_length = math.ceil((max_length * 2) / 10.0) * 10
        return f"VARCHAR({varchar_length})"
    
    if "date" in col_name.lower() or 'time' in col_name.lower():
        
        if ':' in str(df[col_name].iloc[0]):
            return "DATETIME"
        else:
            return "DATE"
    elif "id" in col_name.lower():
        return "VARCHAR(30)"
    elif "name" in col_name.lower():
        if 'pname' in col_name.lower() or 'prod' in col_name.lower():
            return "VARCHAR(800)"
        else:
            return "VARCHAR(500)"
    elif 'url' in col_name.lower():
        return "VARCHAR(2000)"
    elif 'client' in col_name.lower() and 'profile' in col_name.lower() and 'id' in col_name.lower():
        return "VARCHAR(25)"
    elif df[col_name].dtype == 'object' or 'code' in col_name.lower():  
        max_length = df[col_name].astype(str).map(len).max()
        varchar_length = math.ceil((max_length * 2) / 10.0) * 10
        return f"VARCHAR({varchar_length})"
    elif df[col_name].dtype == 'float64' or df[col_name].apply(lambda x: isinstance(x, float)).any():
        return "FLOAT"
    elif df[col_name].dtype == 'int64' or df[col_name].apply(lambda x: isinstance(x, int)).all():
        return "INT"
    else:
        max_length = df[col_name].astype(str).map(len).max()
        varchar_length = math.ceil((max_length * 2) / 10.0) * 10
        return f"VARCHAR({varchar_length})"

def apply_constraints(col_name, data_type):
    return f"{data_type} NULL"

def format_table_name(sheet_name):
    return sheet_name.replace(' ', '_').replace('-', ' ').lower()

def excel_to_sql_create_table(excel_file_path, naming_style, sheet_name):
    table_name = format_table_name(os.path.splitext(os.path.basename(excel_file_path))[0])
    
    try:
        if excel_file_path.endswith('.csv'):
            df = pd.read_csv(excel_file_path)
        elif excel_file_path.endswith('.xlsx'):
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        else:
            print("Unsupported file format. Please provide a CSV or Excel file.")
            return None
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    
    column_definitions = []

    get_column_name_fun = get_column_name if naming_style == 1 else get_column_name_same


    for col in df.columns:
        col_name = get_column_name_fun(col)
        data_type = determine_data_type(df, col)
        column_definition = apply_constraints(col_name, data_type)
        column_definitions.append(f"    {col_name} {column_definition}")

    create_table_stmt = f"CREATE TABLE {table_name} (\n"
    create_table_stmt += ",\n".join(column_definitions)
    create_table_stmt += "\n);"
    
    return create_table_stmt

excel_file_path = r"C:\Users\James\Downloads\sales_data.xlsx" # paste the excel/csv path here.
sheet_name = 0 # paste the sheet name here. Keep it 0 if passing the first sheet.
naming_style = 2  # set naming_style to 1 for defined style and 2 for exact same column name as in excel or csv.
sql_statement = excel_to_sql_create_table(excel_file_path, naming_style, sheet_name)
print(sql_statement)