import pandas as pd
from sqlalchemy import create_engine

# Параметры подключения к базе данных SQLite
#database_path = 'Graf.db'  # Путь к вашей базе данных
table_name = 'data.xlsx'  # Название таблицы, в которую будут записаны данные

# Чтение данных из Excel
excel_file = 'D:\Projects\python\newf.xlsx'  # Путь к вашему Excel-файлу
df = pd.read_excel(excel_file)

# Подключение к базе данных с помощью SQLAlchemy
#engine = create_engine(f'sqlite:///{database_path}')

# Запись данных в таблицу базы данных
#df.to_sql(table_name, con=engine, if_exists='replace', index=False)

#print(f"Данные из {excel_file} успешно загружены в таблицу {table_name} базы данных {database_path}.")
