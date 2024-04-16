import tkinter as tk
from tkinter import ttk, messagebox, Label,Entry,Button,filedialog,LabelFrame
import csv
from datetime import datetime

class Product:
    def __init__(self,name,category,price,stock):
        self.name=name
        self.category=category
        self.price= price
        self.stock = stock

class InventoryApp:
#全体設定    
    def __init__(self,master):
        #全体表示設定。
        self.master = master
        self.master.title( "在庫管理アプリ")
        
        #タブメニュー
        self.tabcontrol = ttk.Notebook(master)
        self.tab1 = ttk.Frame(self.tabcontrol)
        self.tab2 = ttk.Frame(self.tabcontrol)
        self.tab3 = ttk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.tab1,text="商品一覧") 
        self.tabcontrol.add(self.tab2,text="商品登録")
        self.tabcontrol.add(self.tab3,text="持ち出しリスト")
        self.tabcontrol.pack(expand=1,fill="both")      
        
        self.data=[]
        self.products=[]
        
        self.product_list_tab()       
        self.registration_tab()
        self.takeout_list_tab()
                
        self.check_inventory_csv() 
        self.show_product_tab()

#タブ1　商品一覧タブ
    def product_list_tab(self):
        product_list_layout_frame = ttk.Frame(self.tab1)
        product_list_layout_frame.pack()
        
        self.selected_products=[]
        
        self.product_list_section(product_list_layout_frame)
        self.change_stock_section(product_list_layout_frame)         
        self.store_display_section(product_list_layout_frame)
      
    def product_list_section(self,parent_frame):
        #商品一覧
        product_list_frame=ttk.LabelFrame(parent_frame,text="商品一覧")
        product_list_frame.pack(side=tk.TOP,anchor="w",padx=10,pady=10,fill="x")
        
        self.product_tree=ttk.Treeview(product_list_frame,columns=("Name","Category","Price","Stock"),show="headings")
        self.product_tree.heading("Name",text="商品名")
        self.product_tree.heading("Category",text="分類")
        self.product_tree.heading("Price",text="価格")
        self.product_tree.heading("Stock",text="在庫")
        self.product_tree.pack(expand=True,fill="both")

#   在庫数変更機能 
    def change_stock_section(self,parent_frame):
        change_stock_frame = ttk.LabelFrame(parent_frame,text="在庫数の変更")
        change_stock_frame.pack(side=tk.TOP,padx=10,pady=10,fill="x")
        
        self.entry_change_stock=Entry(change_stock_frame)
        self.entry_change_stock.pack(side=tk.LEFT,padx=5,pady=5)
        self.increase_btn=Button(change_stock_frame,text="増やす",command=lambda:self.update_stock("increase"))
        self.increase_btn.pack(side=tk.LEFT,padx=5,pady=5)
        self.decrease_btn=Button(change_stock_frame,text="減らす",command=lambda:self.update_stock("decrease"))
        self.decrease_btn.pack(side=tk.LEFT,padx=5,pady=5)        

    def update_stock(self,action):
        #在庫数の更新
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showerror("Error","商品を選んでください")
            return
        
        item_values = self.product_tree.item(selected_item)["values"]
        product_name = item_values[0]
        
        stock_change = self.entry_change_stock.get()
        
        try:
            stock_change = int(stock_change)
        except ValueError:
            messagebox.showerror("Error","在庫の変更には数字を入れてください")
            return
        
        if action == "decrease":
            current_stock = int(item_values[3])
            if current_stock - stock_change < 0:
                messagebox.showerror("エラー", "在庫がマイナスになります")
                return
            stock_change= -stock_change
        
        updated_rows = []
        
        with open ("inventory.csv","r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["Name"] == product_name:
                    row["Stock"] = int(row["Stock"])+stock_change
                updated_rows.append(row)
                    
        with open ("inventory.csv","w",newline="") as csvfile:
            fieldnames=["Name","Category","Price","Stock"]
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
            writer.writeheader()
            for row in updated_rows:
                writer.writerow(row)
        
        action_label = "在庫を追加" if action == "increase" else "在庫を減らす"
        
        self.save_log_to_csv(action_label,product_name,stock_change)

        self.show_product_tab()

#   店頭に並べる商品リスト  
    def store_display_section(self,parent_frame):
        #店頭に並べる商品リスト
        self.store_dispay_frame = ttk.LabelFrame(parent_frame,text="店頭に並べる商品")
        self.store_dispay_frame.pack(side=tk.TOP,padx=10,pady=10,fill="x")

        self.store_tree = ttk.Treeview(self.store_dispay_frame,columns=("Name","Category","Price","Stock"),show="headings")
        self.store_tree.heading("Name",text="商品名")
        self.store_tree.heading("Category",text="分類")
        self.store_tree.heading("Price",text="価格")
        self.store_tree.heading("Stock",text="在庫")
        self.store_tree.pack(expand=True,fill="both")
        
        self.add_to_store_btn = Button(self.store_dispay_frame,text="追加",command=self.add_to_store_display)
        self.add_to_store_btn.pack(side=tk.LEFT,padx=5,pady=5)
        self.delete_from_display_btn =Button(self.store_dispay_frame,text="削除",command=self.delete_from_display)
        self.delete_from_display_btn.pack(side=tk.LEFT,padx=5,pady=5)
        self.takeout_btn = Button(self.store_dispay_frame,text="持ち出し",command=self.takeout_product)
        self.takeout_btn.pack(side=tk.LEFT,padx=5,pady=5)
        
    def add_to_store_display(self):
        #選択した商品を店頭に並べるリストに追加
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showerror("エラー","商品を選択してください")
            return
        
        item_values = self.product_tree.item(selected_item)["values"]
        self.selected_products.append(item_values)
        self.store_tree.insert("","end",values=item_values)
        
    def delete_from_display(self):
        #店頭に並べるリストから削除
        selected_item = self.store_tree.selection()
        if not selected_item:
            messagebox.showerror("エラー","削除する商品を選択してください")
            return
        
        item_values = self.store_tree.item(selected_item)["values"]
        self.selected_products.remove(item_values)
        self.store_tree.delete(selected_item)       

    def takeout_product(self):
        bring_list = []  # 商品情報を格納するリスト
        for item_values in self.selected_products:
            bring_list.append(item_values)  # 商品情報をリストに追加

        # 重複した商品を削除
        for item_values in self.selected_products:
            item_name = item_values[0]  # 商品名を取得
            items = self.store_tree.get_children()
            for item in items:
                if self.store_tree.item(item, "values")[0] == item_name:
                    self.store_tree.delete(item)
                    break

        # selected_productsを初期化
        self.selected_products = []
        
        for item_values in bring_list:
            self.add_to_takeout_list(item_values)
    
    def add_to_takeout_list(self, item_values):
        item_name = item_values[0]
        item_category = item_values[1]  # 商品の分類を取得
        
        # 持ち出しリストに重複がないか確認し、重複する場合は追加を行わない
        for child in self.takeout_list_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                label = child.winfo_children()[1]  # 2番目の子要素は商品名のLabelウィジェット
                if label.cget("text") == item_name:
                    return
        
        # 商品を持ち出しリストに追加
        product_frame = ttk.Frame(self.takeout_list_frame)
        product_frame.pack(anchor="w", padx=10, pady=5, fill="x")

        takeout_checked = tk.BooleanVar(value=False)
        takeout_check_box = tk.Checkbutton(product_frame, variable=takeout_checked)
        takeout_check_box.pack(side=tk.LEFT)
        
        # 商品名を表示するラベル
        product_name_label = Label(product_frame,width=30,anchor="w", text=item_name)
        product_name_label.pack(side=tk.LEFT, padx=10)
         # 分類を表示するラベル
        category_label = Label(product_frame,width=15,anchor="w", text=item_category)
        category_label.pack(side=tk.LEFT, padx=5)       
        
        status_label = Label(product_frame,width=10, text="準備中　")
        status_label.pack(side=tk.RIGHT, padx=10)
        
        quantity_entry = Entry(product_frame, width=5)
        quantity_entry.pack(side=tk.RIGHT)
    

        def update_status(event, status_label=status_label, takeout_checked=takeout_checked):
            status_label.config(text="準備中　" if takeout_checked.get() else "持出済み")

        takeout_check_box.bind("<Button-1>", update_status)
        

        
#タブ2　商品登録タブ        
    def registration_tab(self):
        #タブ1 商品登録画面
        self.registration_layout_frame = ttk.Frame(self.tab2)
        self.registration_layout_frame.pack(side=tk.TOP,anchor="w",padx=10,pady=10,fill="x")
        
        self.product_registration_section(self.registration_layout_frame)
        self.file_op_section(self.registration_layout_frame)
        
    def product_registration_section(self,parent_frame):
        #入力欄
        self.registration_frame = LabelFrame(parent_frame,text="商品登録")
        self.registration_frame.pack(side=tk.TOP,anchor="w",padx=5,pady=5,fill="x")
        
        self.label_name = Label(self.registration_frame, text="商品名")
        self.label_name.grid(row=0,column=0,sticky="w")
        self.label_category = Label(self.registration_frame,text="分類")
        self.label_category.grid(row=1,column=0, sticky="w")
        self.label_price = Label(self.registration_frame, text="価格")
        self.label_price.grid(row=2,column=0,sticky="w")
        self.label_stock = Label(self.registration_frame,text="在庫")
        self.label_stock.grid(row=3,column=0,sticky="w")
        
        self.entry_name = Entry(self.registration_frame)
        self.entry_name.grid(row=0,column=1)
        self.entry_category = Entry(self.registration_frame)
        self.entry_category.grid(row=1,column=1)
        self.entry_price = Entry(self.registration_frame)
        self.entry_price.grid(row=2,column=1)
        self.entry_stock = Entry(self.registration_frame)
        self.entry_stock.grid(row=3,column=1)
        
        self.submit_btn = Button(self.registration_frame,text="商品を追加",command=self.add_product)
        self.submit_btn.grid(row=4,columnspan=1)
        
        self.entry_name.bind('<Return>', lambda event=None: self.add_product())
        self.entry_category.bind('<Return>', lambda event=None: self.add_product())
        self.entry_price.bind('<Return>', lambda event=None: self.add_product())
        self.entry_stock.bind('<Return>', lambda event=None: self.add_product())

    def add_product(self):
        name = self.entry_name.get()
        category = self.entry_category.get()
        price = self.entry_price.get()
        stock = self.entry_stock.get()
        
        try:
            price= int(price)
            stock = int(stock)
        
        except ValueError:
            messagebox.showerror("Error","価格と在庫は数字を入れてください")
            return
        
        new_product = Product(name, category, price, stock)
        self.products.append(new_product)  # self.products に商品情報を追加
        self.save_product_to_csv(new_product)
        messagebox.showinfo("完了","新しい商品を追加しました")
        
        self.entry_name.delete(0,tk.END)
        self.entry_category.delete(0,tk.END)
        self.entry_price.delete(0,tk.END)
        self.entry_stock.delete(0,tk.END)
        
        self.save_log_to_csv("新規登録",name,stock)
        self.show_product_tab()

    def file_op_section(self,parent_frame):
        self.file_op_frame = LabelFrame(parent_frame,text="ファイル操作")
        self.file_op_frame.pack(side=tk.TOP,anchor="w",padx=5,pady=5)
        
        self.file_load_btn = Button(self.file_op_frame,text="読み込み",command=self.load_file)
        self.file_load_btn.pack(side = tk.LEFT,padx=5,pady=5)
        
        self.file_output_btn =Button(self.file_op_frame,text = "保存",command=self.output_file)
        self.file_output_btn.pack(side = tk.LEFT,padx=5,pady=5)
        
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files","*csv")])
        if file_path:
            try:
                with open(file_path,newline="") as csvfile:
                    reader=csv.reader(csvfile)
                    next(reader) #ヘッダー行スキップ
                    for row in reader:
                        name,category,price,stock = row
                        price = int(price)
                        stock = int(stock)
                        existing_product = self.same_name_category(name,category)
                        if existing_product:
                            existing_product.stock=stock
                        else:
                            new_product = Product(name,category,price,stock)
                            self.products.append(new_product)
                            self.save_product_to_csv(new_product)
                messagebox.showinfo("成功","ファイルの読み込みが完了しました")
                self.show_product_tab()#表示の更新
            except Exception as e:
                messagebox.showinfo("エラー",f"ファイルの読み込みに失敗しました:\n{e}")
        
    def same_name_category(self,name,category):
        for product in self.products:
            if product.name == name and product.category == category:
                return product
        return None
            
    def output_file(self):
        # "{現在時刻}+商品一覧"のファイル名でcsv保存
        current_time = datetime.now().strftime("%y%m%d_%H%M")
        file_name = f"{current_time}時点_商品一覧.csv"
        
        try:
            with open("inventory.csv", "r", newline="") as input_file:
                with open(file_name, "w", newline="") as output_file:
                    reader = csv.reader(input_file)
                    writer = csv.writer(output_file)
                    for row in reader:
                        writer.writerow(row)
            
            messagebox.showinfo("成功", f"データを{file_name}に保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの保存に失敗しました:\n{e}")

#タブ3　持ち出しリストタブ
    def takeout_list_tab(self):
        takeout_list_layout_frame = ttk.Frame(self.tab3)
        takeout_list_layout_frame.pack(side=tk.TOP,padx=10,pady=10,fill="both")

        self.save_takeout_section(takeout_list_layout_frame)
        self.takeout_list_section(takeout_list_layout_frame)     
   
                
    def takeout_list_section(self,parent_frame):
        self.takeout_list_frame = ttk.LabelFrame(parent_frame,text="持ち出しリスト")
        self.takeout_list_frame.pack(side=tk.TOP,padx=10,pady=10,fill="both",expand=True)    
    
    def save_takeout_section(self,parent_frame):
        self.save_takeout_frame =ttk.LabelFrame(parent_frame,text="リストを管理") 
        self.save_takeout_frame.pack(side=tk.TOP,anchor="w",padx=10,pady=10,fill="both")
        
        self.save_takeout_btn = Button(self.save_takeout_frame,text="保存",command=self.save_takeout)   
        self.save_takeout_btn.pack(side=tk.LEFT,padx=10)
        self.load_takeout_btn = Button(self.save_takeout_frame,text="読み込み",command=self.load_takeout)  
        self.load_takeout_btn.pack(side=tk.LEFT)
    def load_takeout(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, "r", newline="") as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if row:  # 空行をスキップ
                            product_name, category, quantity = row
                            self.add_to_takeout_from_csv(product_name, category, quantity)
                messagebox.showinfo("成功", "持ち出しリストを読み込みました")
            except Exception as e:
                messagebox.showerror("エラー", f"持ち出しリストの読み込み中にエラーが発生しました: {e}")

    def add_to_takeout_from_csv(self, product_name, category, quantity):
        # 商品を持ち出しリストに追加
        product_frame = ttk.Frame(self.takeout_list_frame)
        product_frame.pack(anchor="w", padx=10, pady=5, fill="x")

        takeout_checked = tk.BooleanVar(value=False)
        takeout_check_box = tk.Checkbutton(product_frame, variable=takeout_checked)
        takeout_check_box.pack(side=tk.LEFT)
        
        # 商品名を表示するラベル
        product_name_label = Label(product_frame, width=30, anchor="w", text=product_name)
        product_name_label.pack(side=tk.LEFT, padx=10)
         # 分類を表示するラベル
        category_label = Label(product_frame, width=15, anchor="w", text=category)
        category_label.pack(side=tk.LEFT, padx=5)       
        
        status_label = Label(product_frame, width=10, text="準備中　")
        status_label.pack(side=tk.RIGHT, padx=10)
        
        quantity_entry = Entry(product_frame, width=5)
        quantity_entry.insert(tk.END, quantity)  # 数量を設定
        quantity_entry.pack(side=tk.RIGHT)

        def update_status(event, status_label=status_label, takeout_checked=takeout_checked):
            status_label.config(text="準備中　" if takeout_checked.get() else "持出済み")

        takeout_check_box.bind("<Button-1>", update_status)

    def save_takeout(self):
        takeout_items = []
        # "{現在時刻}+商品一覧"のファイル名でcsv保存
        current_time = datetime.now().strftime("%y%m%d_%H%M")
        file_name = f"{current_time}時点_持ち出しリスト.csv"
        
        # takeout_list_frame内の子要素を取得し、商品情報をリストに格納する
        for child in self.takeout_list_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                product_name = child.winfo_children()[1].cget("text")  # 商品名を取得
                label_text = child.winfo_children()[2].cget("text")
                quantity_entry = child.winfo_children()[-1]  # Entryウィジェットは最後の要素にある
                quantity = quantity_entry.get()  # 入力された数量を取得
                if not quantity:
                    messagebox.showwarning("警告", "数量が入力されていません。持ち出しリストに追加する場合は数量を入力してください。")
                    return
                if quantity.isdigit():  # 数量が数字であれば
                    quantity = int(quantity)
                
                stock = self.get_stock(product_name)
                if quantity > stock:
                    messagebox.showerror("エラー", f"在庫が足りません。商品名: {product_name}, 在庫数: {stock}")
                    return
                takeout_items.append((product_name, label_text, quantity))
                
        # CSVファイルに書き出す
        try:
            with open(file_name, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                for item in takeout_items:
                    writer.writerow([item[0], item[1], item[2]])  # 商品名、分類、数量をCSVファイルに書き出す
            messagebox.showinfo("成功", "持ち出しリストを保存しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました: {e}")

    def get_stock(self, product_name):
        # 商品名をキーにして在庫数を取得
        for item in self.product_tree.get_children():
            item_values = self.product_tree.item(item, "values")
            if item_values[0] == product_name:
                stock = int(item_values[3])
                return stock
        return 0  # 商品名が見つからない場合は在庫数 0 を返す          

#基本機能　記録・表示まわり  
    def check_inventory_csv(self):
        try:
            with open("inventory.csv","r",newline="") as csvfile:
                reader = csv.reader(csvfile)
                if not any(row for row in reader):
                    self.write_header_to_csv()
                    
        except FileNotFoundError:
            self.write_header_to_csv()
    
    def write_header_to_csv(self):
        header = ["Name","Category","Price","Stock"]
        with open("inventory.csv","w",newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
    
    def show_product_tab(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
            
        products = []
        try:
            with open ("inventory.csv",newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row['Name']
                    category = row["Category"]
                    price = int(row["Price"])
                    stock = int(row["Stock"])
                    products.append((name,category,price,stock))
            
            sorted_products = sorted(products, key=lambda x:x[1])
        
            for product in sorted_products:
                self.product_tree.insert("","end",values=product)
        
        except FileNotFoundError:
            messagebox.showwarning("ファイルが見つかりません","Inventory file not found. Showing empty list.")
                                          
    def save_product_to_csv(self, product):
        with open('inventory.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([product.name, product.category, product.price, product.stock])
    
    def save_log_to_csv(self,action,product_name,quantity):
        timestamp =datetime.now().strftime("%y%m%d %H:%M:%S")
        with open ("log.csv","a",newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp,action,product_name,quantity])
    
#起動
def main():
    root=tk.Tk()
    app= InventoryApp(root)
    root.mainloop()

if __name__=="__main__":
    main()
