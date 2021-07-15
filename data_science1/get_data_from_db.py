from connect_database import ConnectDatabase
import pandas as pd

class GetDataFromDB(ConnectDatabase):

    def get_limit_products_from_db(self):
        connection_db = self.connect_db()
        product_query = """ select id as product_id, master_product_id, name from products where master_product_id is not NULL and id between 200000 and 300000 order by id limit 10 """
        products_df = pd.read_sql(product_query, connection_db)
        connection_db.close()
        return products_df

    def get_limit_master_products_from_db(self):
        connection_db = self.connect_db()
        master_product_query = """ select distinct on (id) id as master_product_id, name from master_products where id in 
                                (select master_product_id from products where master_product_id is not NULL and id between 300000 and 400000 order by id limit 10) """
        master_products_df = pd.read_sql(master_product_query, connection_db)
        connection_db.close()
        return master_products_df

    def get_all_master_products_from_db(self):
        connection_db = self.connect_db()
        master_product_query = """ select id as master_product_id, name from master_products """
        master_products_df = pd.read_sql(master_product_query, connection_db)
        connection_db.close()
        return master_products_df

    def get_specific_products_and_master_products_from_db(self):
        connection_db = self.connect_db()
        product_query = """ select products.id as product_id, products.master_product_id, products.name as name, master_products.name as must_match_master_product_actual_name from products join 
                            master_products on master_products.id = products.master_product_id
                            where products.master_product_id is not NULL and products.id between 250000 and 300000 order by products.id limit 100 """
        master_product_query = """ (select master_products.id as master_product_id, master_products.name from master_products where master_products.id in 
                                    (select products.master_product_id from products where products.master_product_id is not NULL and products.id between 250000 and 300000 order by products.id limit 100))
                                """
        # union (select id as master_product_id, name from master_products limit 100) 
        products_df = pd.read_sql(product_query, connection_db)
        master_products_df = pd.read_sql(master_product_query, connection_db)
        connection_db.close()
        return [products_df, master_products_df]