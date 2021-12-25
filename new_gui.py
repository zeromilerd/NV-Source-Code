from logging import root
import threading
from tkinter import (
    Tk,
    Frame,
    Label,
    Button,
    Entry,
    Message,
    CENTER,
    Menu,
    Menubutton,
    StringVar,
    RAISED,
    messagebox,
)
from tkinter import *
from tkinter import ttk
import tkinter as tk
from eth_utils.decorators import T

from numpy.lib.function_base import diff
from eth_wallet.configuration import (
    Configuration,
)
from eth_wallet.api import (
    WalletAPI,
)
from eth_wallet.ui.page import (
    Page
)
from ZeroVOperations import getZeroVDevice
import getpass
import time
import sys
import os
import io
import cv2
from PIL import Image, ImageTk
from cryptography.fernet import Fernet

from VideoAuthPkg import FaceMod

eKey = b'AqYASHHw6ZiTQmtzFeu8iOTpG6KXLgoSGjBp4lh7_GQ='
fernet = Fernet(eKey)

L_MSG = None

default_path = "/.config/.eth-wallet"
if getZeroVDevice() == None:
    sys.exit()
#CONFIG_DIR = '/home/viprush/nvConfig_demo/.eth-wallet'
CONFIG_DIR = getZeroVDevice()['devicePath'] + default_path
#INITIAL_CONFIG = {'keystore_location': '/home/viprush/nvConfig_demo/.eth-wallet', 'keystore_filename': '/keystore', 'eth_address': '', 'public_key': '', 'network': 3, 'contracts': {}}
INITIAL_CONFIG = {'keystore_location': CONFIG_DIR, 'keystore_filename': '/keystore', 'eth_address': '', 'public_key': '', 'network': 3, 'contracts': {}}

ValidBlinkCount = 2
TIMEOUT = 40


class VideoAuthPage(Page):
    
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        self.panel = Label(self)
        self.panel.pack()
        self.VA = FaceMod.VideoAuth()
        self.authStatus = False
        self.startTime = time.time()
            
        #B_eject = ttk.Button(self, text = "OK", command = self.nvquit)
        #B_eject.pack()

    def __getBlankFeed(self):
        cv2image = None
        cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
        cv2image = cv2.flip(cv2image, 1)
        self.current_image = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=self.current_image)
        self.panel.imgtk = imgtk
        self.panel.config(image=imgtk)

    def getDemoMethod(self):
        print("Demo Video")

    def displayVideo(self):
        try:
            #time.sleep(0.1)
            img, n = self.VA.get_blank_feed_with_faces()
            print(n)
            if n == 1:
                img, name, total = self.VA.get_identity_feed()
                print(name)
                if total >= ValidBlinkCount:
                    self.authStatus = True
            cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            self.current_image = Image.fromarray(cv2image)
            #imgtk = ImageTk.PhotoImage(image=self.current_image)
            imgtk = ImageTk.PhotoImage(self.current_image.resize((500, 350)))
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
            self.currentTime = time.time()
            diff = self.currentTime - self.startTime
            #if diff > TIMEOUT:
            #    root.destroy()
            return self.authStatus, diff
        
        except Exception as e:
            print(e)

    def releaseResourses(self):
        del self.VA

    def __del__(self):
        print("Deleted Video Window")

        

class VideoNewPage(Page):
    
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        self.panel = Label(self)
        self.panel.pack()
        self.VA = FaceMod.VideoAuth()
        self.accountCreated = False
        self.startTime = time.time()
            
        B_capture = ttk.Button(self, text = "Capture & Save", command = self.saveImage)
        B_capture.pack()

    def displayNewVideo(self):
        try:
            #time.sleep(0.1)
            img, n = self.VA.get_blank_feed_with_faces()
            print(n)
            cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            self.current_image = Image.fromarray(cv2image)
            #imgtk = ImageTk.PhotoImage(image=self.current_image)
            imgtk = ImageTk.PhotoImage(self.current_image.resize((470, 300)))
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
            return self.accountCreated

        except Exception as e:
            print(e)

    def saveImage(self):
        buf = io.BytesIO()
        self.current_image.convert('RGB').save(buf, format='JPEG')
        b = buf.getvalue()
        IMG_DIR_PATH = getZeroVDevice()['devicePath'] + default_path + '/profiles'
        os.makedirs(IMG_DIR_PATH)
        file = open(IMG_DIR_PATH + "/NV_User.profile", 'wb')
        file.write(fernet.encrypt(b))
        file.close()
        self.accountCreated = True

    def releaseResourses(self):
        del self.VA

    def __del__(self):
        print("Deleted Video Window")















class NewWalletPage(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.configuration = None
        self.api = WalletAPI()
        self.wallet = None

        lbl_pswd = Label(self,
                         text='\nSet Password for New Wallet:',
                         font=('arial', 14, 'bold'), bg = 'white')
        lbl_pswd.pack()

        entry_password = ttk.Entry(self,
                               show="*",
                               font=(None, 16),
                               width=15,
                               justify=CENTER)
        entry_password.pack()
        l = Label(self, text = "", bg = 'white').pack()
        btn_create_wallet = ttk.Button(self,
                                   text="Generate",
                                   command=lambda: self.create_wallet(btn_create_wallet,
                                                                      entry_password.get()))

        btn_create_wallet.pack()

    def create_wallet(self, btn_create_wallet, password):
        """
        Create new wallet
        :param btn_create_wallet: generate button which change text and functionality
        :param password: passphrase from the user
        :return:
        """
        self.configuration = Configuration(config_dir = CONFIG_DIR, initial_config = INITIAL_CONFIG).load_configuration()
        self.wallet = self.api.new_wallet(self.configuration, password)

        lbl_remember_words = Label(self,
                                   text='\nRestore sentence:',
                                   bg = 'white')
        lbl_remember_words.pack()

        lbl_mnemonic = Message(self,
                               text=self.wallet.get_mnemonic(),
                               justify=CENTER,
                               borderwidth=10,
                               background='light blue')
        lbl_mnemonic.pack()
        
        btn_copy_address = ttk.Button(self,
                                  text="Copy Restore Sentence",
                                  command=self.copy_address)
        btn_copy_address.pack()
        
        btn_create_wallet.configure(text="Continue",
                                    command=self.navigate_insert_page)

    def navigate_insert_page(self):
        """
        Navigate to home page
        :return:
        """
        info_page = InsertPage(self)
        info_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        info_page.show()
        
    def copy_address(self):
        """Add Sentence to the clipboard"""
        self.clipboard_clear()  # clear clipboard contents
        self.clipboard_append(self.wallet.get_mnemonic())  # append new value to clipbaoard


class TransactionPage(Page):

    def __init__(self, *args, **kwargs):
        global L_MSG
        Page.__init__(self, *args, **kwargs)

        self.configuration = Configuration(config_dir = CONFIG_DIR, initial_config = INITIAL_CONFIG).load_configuration()
        self.api = WalletAPI()
        self.tokens = self.api.list_tokens(self.configuration)
        self.eth_balance, _ = self.api.get_balance(self.configuration)

        def change_token(token):
            if token == 'ETH':
                self.eth_balance, _ = self.api.get_balance(self.configuration)
            else:
                self.eth_balance, _ = self.api.get_balance(self.configuration, token)

            balance.set(str(self.eth_balance) + ' ' + token)

        token_symbol = StringVar()
        token_symbol.set('ETH')
        balance = StringVar()
        balance.set(str(self.eth_balance) + ' ' + token_symbol.get())

        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        mb = Menubutton(self,
                        textvariable=token_symbol,
                        relief=RAISED)
        mb.grid(row = 0, column = 1, columnspan = 2, sticky = 'we')
        mb.menu = Menu(mb, tearoff=0)
        mb["menu"] = mb.menu
        mb.menu.add_radiobutton(label="ETH",
                                variable=token_symbol,
                                value='ETH',
                                command=lambda: change_token(token_symbol.get()))
        for token in self.tokens:
            mb.menu.add_radiobutton(label=token,
                                    variable=token_symbol,
                                    value=token,
                                    command=lambda: change_token(token_symbol.get()))
        mb.grid(row = 0, column = 1, columnspan = 2, sticky = 'we')

        label = Label(self,
                      textvariable=balance,
                      width=60, bg = 'white', fg = 'red',
                      font=(None, 30, 'bold'))
        label.grid(row = 1, column = 1, columnspan = 2, sticky = 'we')

        lbl_address = Label(self,
                            text="To address:", bg = 'white',
                            font=('airal', 13, 'bold'))
        lbl_address.grid(row = 2, column = 1, sticky = 'w', padx = 10, pady = 10)

        entry_address = ttk.Entry(self,
                              width=30)
        entry_address.grid(row = 2, column = 2, sticky = 'w', padx = 10, pady = 10)

        lbl_amount = Label(self,
                           text="Amount:", bg = 'white',
                           font=('airal', 13, 'bold'))
        lbl_amount.grid(row = 3, column = 1, sticky = 'w', padx = 10, pady = 10)

        entry_amount = ttk.Entry(self,
                             width=30)
        entry_amount.grid(row = 3, column = 2, sticky = 'w', padx = 10, pady = 10)

        lbl_passphrase = Label(self,
                               text="Wallet Password:", bg = 'white',
                               font=('airal', 13, 'bold'))
        lbl_passphrase.grid(row = 4, column = 1, sticky = 'w', padx = 10, pady = 10)

        entry_passphrase = ttk.Entry(self,
                                 show = '*',
                                 width=30)
        entry_passphrase.grid(row = 4, column = 2, sticky = 'w', padx = 10, pady = 10)

        l = Label(self, text = "", bg = 'white')
        l.grid(row = 5, column = 1, padx = 10, pady = 10)

        btn_back = ttk.Button(self,
                          text="Back",
                          command=self.navigate_home_page)
        btn_back.grid(row = 10, column = 1, sticky = 'n', padx = 10, pady = 10)

        btn_send = ttk.Button(self,
                          text="Send",
                          command=lambda: self.send_transaction(entry_address.get(),
                                                                entry_amount.get(),
                                                                entry_passphrase.get(),
                                                                token_symbol.get()))
        btn_send.grid(row = 10, column = 2, sticky = 'n', padx = 10, pady = 10)
        
        L_MSG = Label(self, text = "", bg = 'white')
        L_MSG.grid(row = 12, column = 1, columnspan = 2, padx = 10, pady = 10)

        

    def navigate_home_page(self):
        """
        Navigate to home page
        :return:
        """
        info_page = HomePage(self)
        info_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        info_page.show()
        self.place_forget()

    def send_transaction(self, to, value, password, token):
        """
        Send transaction
        :return:
        """
        if token == 'ETH':
            tx_thread = TransactionThread(configuration=self.configuration,
                                          password=password,
                                          to=to,
                                          value=value,
                                          token=None)
        else:
            tx_thread = TransactionThread(configuration=self.configuration,
                                          password=password,
                                          to=to,
                                          value=value,
                                          token=token)
        tx_thread.start()


class TransactionThread(threading.Thread):
    def __init__(self, configuration, password, to, value, token=None):
        threading.Thread.__init__(self)
        self.api = WalletAPI()
        self.configuration = configuration
        self.password = password
        self.to = to
        self.value = value
        self.token = token

    def run(self):
        global L_MSG
        if self.token is None:
            # send ETH transaction
            tx_hash, tx_cost_eth = self.api.send_transaction(self.configuration,
                                                             self.password,
                                                             self.to,
                                                             self.value)
        else:
            # send erc20 transaction
            tx_hash, tx_cost_eth = self.api.send_transaction(self.configuration,
                                                             self.password,
                                                             self.to,
                                                             self.value,
                                                             self.token)
        #messagebox.showinfo("Transaction mined!", "Transaction was mined for " + str(tx_cost_eth) + "ETH fee.")
        L_MSG.config(text = "Transaction was mined for " + str(tx_cost_eth) + "ETH fee.")
        time.sleep(5)
        L_MSG.config(text = "")

        
class AddTokenPage(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.configuration = Configuration(config_dir = CONFIG_DIR, initial_config = INITIAL_CONFIG).load_configuration()
        self.api = WalletAPI()

        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        lbl_symbol = Label(self,
                           text="Contract's symbol:", bg = 'white',
                           font=(None, 13, 'bold'))
        lbl_symbol.grid(row = 1, column = 1, sticky = 'w', padx = 10, pady = 10)

        entry_symbol = ttk.Entry(self,
                             width=30)
        entry_symbol.grid(row = 1, column = 2, sticky = 'w', padx = 10, pady = 10)

        lbl_address = Label(self,
                            text="Contract's address:", bg = 'white',
                            font=(None, 13, 'bold'))
        lbl_address.grid(row = 2, column = 1, sticky = 'w', padx = 10, pady = 10)

        entry_address = ttk.Entry(self,
                              width=30)
        entry_address.grid(row = 2, column = 2, sticky = 'w', padx = 10, pady = 10)

        l = Label(self, text = "", bg = 'white')
        l.grid(row = 5, column = 1, padx = 10, pady = 10)

        btn_back = Button(self,
                          text="Back",
                          command=self.navigate_home_page)
        btn_back.grid(row = 10, column = 1, sticky = 'n', padx = 10, pady = 10)
        
        btn_add = ttk.Button(self,
                          text="Add",
                          command=lambda: self.add_token(entry_symbol.get(), entry_address.get()))
        btn_add.grid(row = 10, column = 2, sticky = 'n', padx = 10, pady = 10)
        

    def navigate_home_page(self):
        """
        Navigate to home page
        :return:
        """
        info_page = HomePage(self)
        info_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        info_page.show()
        self.place_forget()
        
    def add_token(self, symbol, contract):
        """
        Add new token and navigate to home page
        :param symbol: token symbol
        :param contract: contracts address
        :return:
        """
        self.api.add_contract(self.configuration, symbol, contract)
        info_page = HomePage(self)
        info_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        info_page.show()
        self.place_forget()





class InsertPage(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        L = Label(self, text = "\n\nPlease Eject and Re-insert NatiVault\n", bg = 'white', font = ('arial', 18, 'bold'), fg = 'blue')
        L.pack()
        
        B_eject = ttk.Button(self, text = "OK", command = self.nvquit)
        B_eject.pack()
        
        
        
    @staticmethod
    def nvquit():
        root.grab_release()
        root.destroy()




class HomePage(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.configuration = Configuration(config_dir = CONFIG_DIR, initial_config = INITIAL_CONFIG).load_configuration()
        self.api = WalletAPI()
        self.tokens = self.api.list_tokens(self.configuration)
        self.eth_balance, self.address = self.api.get_balance(self.configuration)

        def refresh():
            change_token(token_symbol.get())

        def change_token(token):
            if token == 'ETH':
                self.eth_balance, self.address = self.api.get_balance(self.configuration)
            else:
                self.eth_balance, self.address = self.api.get_balance(self.configuration, token)
            balance.set(str(self.eth_balance) + ' ' + token)

        token_symbol = StringVar()
        token_symbol.set('ETH')
        balance = StringVar()
        balance.set(str(self.eth_balance) + ' ' + token_symbol.get())

        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        mb = Menubutton(self,
                        width=60,
                        textvariable=token_symbol,
                        relief=RAISED)
        mb.grid(row = 0, column = 1, columnspan = 2, sticky = 'we')
        mb.menu = Menu(mb, tearoff=0)
        mb["menu"] = mb.menu
        mb.menu.add_radiobutton(label="ETH",
                                variable=token_symbol,
                                value='ETH',
                                command=lambda: change_token(token_symbol.get()))
        for token in self.tokens:
            mb.menu.add_radiobutton(label=token,
                                    variable=token_symbol,
                                    value=token,
                                    command=lambda: change_token(token_symbol.get()))
        mb.menu.add_radiobutton(label="Add new token ...",
                                command=self.navigate_add_token_page)
        mb.grid(row = 0, column = 1, columnspan = 2, sticky = 'we')

        label_address_lbl = Label(self,
                                  text='\nAddress:',
                                  width=60, bg = 'white',
                                  font=(None, 10))
        label_address_lbl.grid(row = 1, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'we')
        label_address = Label(self,
                              text=self.address,
                              width=60, bg = 'white', fg = 'blue',
                              font=(None, 10, 'bold'))
        label_address.grid(row = 2, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

        label_balance = Label(self,
                              textvariable=balance,
                              width=60, bg = 'white', fg = 'red',
                              font=(None, 30, 'bold'))
        label_balance.grid(row = 3, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'n')

        btn_refresh = ttk.Button(self,
                             text="Refresh",
                             command=refresh)
        btn_refresh.grid(row = 10, column = 1, padx = 10, pady = 10, sticky = 'we')

        btn_copy_address = ttk.Button(self,
                                  text="Copy address",
                                  command=self.copy_address)
        btn_copy_address.grid(row = 10, column = 2, padx = 10, pady = 10, sticky = 'we')

        btn_send_transaction = ttk.Button(self,
                                      text="Send Transaction",
                                      command=self.navigate_transaction_page)
        btn_send_transaction.grid(row = 11, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

        B_EXIT = ttk.Button(self, text = "Exit", command = self.nvquit)
        #B_EXIT.grid(row = 15, column = 1, padx = 10, pady = 10, sticky = 'we')


    def navigate_transaction_page(self):
        """
        Navigate to transaction page
        :return:
        """
        print("Navigated")
        self.place_forget()
        global i, nvpass_auth, AuthStatus
        i = 0
        nvpass_auth = False
        AuthStatus = False
        init_auth(NextWindow = TransactionPage)
        #transaction_page = TransactionPage(self)
        #transaction_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        #transaction_page.show()

    def navigate_add_token_page(self):
        """
        Navigate to transaction page
        :return:
        """
        add_token_page = AddTokenPage(self)
        add_token_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        add_token_page.show()

    def copy_address(self):
        """Add address to the clipboard"""
        self.clipboard_clear()  # clear clipboard contents
        self.clipboard_append(self.address)  # append new value to clipbaoard

    @staticmethod
    def nvquit():
        root.grab_release()
        root.destroy()


class RestoreWalletPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        self.configuration = Configuration(config_dir = CONFIG_DIR, initial_config = INITIAL_CONFIG).load_configuration()
        self.api = WalletAPI()
        
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)
        
        L = Label(self, text = "Restore NatiVault Account", bg = 'white', font = ('arial', 20, 'bold'), fg = 'red')
        L.grid(row = 1, column = 1, columnspan = 2, padx = 20, pady = 20, sticky = 'we')
        
        L = Label(self, text = "Recovery Seed:", bg = 'white', font = ('arial', 13, 'bold'))
        L.grid(row = 3, column = 1, padx = 10, pady = 10, sticky = 'w')
        E_words = ttk.Entry(self, width = 30, show = '#')
        E_words.grid(row = 3, column = 2, padx = 10, pady = 10, sticky = 'we')
        
        L = Label(self, text = "Wallet Password:", bg = 'white', font = ('arial', 13, 'bold'))
        L.grid(row = 4, column = 1, padx = 10, pady = 10, sticky = 'w')
        E_pswd = ttk.Entry(self, width = 30, show = '*')
        E_pswd.grid(row = 4, column = 2, padx = 10, pady = 10, sticky = 'we')
        
        B = ttk.Button(self, text = "Restore Now", command = lambda: self.recover_wallet(E_words.get(), E_pswd.get()))
        B.grid(row = 10, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'n')
        
    def recover_wallet(self, words, password):
        w = self.api.restore_wallet(self.configuration, words, password)
        
        New_HomePage = HomePage(self)
        New_HomePage.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        New_HomePage.show()
        


class InitWindow(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        self.grid_columnconfigure(1, weight = 1)
        
        L = Label(self, text = "Welcome to NatiVault", bg = 'white', font = ('arial', 20, 'bold'), fg = 'red')
        L.grid(row = 1, column = 1, padx = 20, pady = 20, sticky = 'we')
        
        B_NewWallet = ttk.Button(self, text = "New Wallet", command = self.navigate_new_wallet_page)
        B_NewWallet.grid(row = 3, column = 1, padx = 20, pady = 10, sticky = 'we')
        
        B_RestoreWallet = ttk.Button(self, text = "Restore Wallet", command = self.navigate_restore_wallet_page)
        B_RestoreWallet.grid(row = 4, column = 1, padx = 20, pady = 10, sticky = 'we')

        B_EXIT = ttk.Button(self, text = "Exit", command = self.nvquit)
        #B_EXIT.grid(row = 5, column = 1, padx = 20, pady = 10, sticky = 'we')

    def navigate_new_wallet_page(self):
        New_WalletPage = NewWalletPage(self)
        New_WalletPage.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        New_WalletPage.show()
        
    def navigate_restore_wallet_page(self):
        Restore_WalletPage = RestoreWalletPage(self)
        Restore_WalletPage.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        Restore_WalletPage.show()

    @staticmethod
    def nvquit():
        root.grab_release()
        root.destroy()
        



class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self.configuration = Configuration(config_dir = CONFIG_DIR, initial_config = INITIAL_CONFIG)
        self.api = WalletAPI()
        self.wallet = None

        if self.configuration.is_configuration():
            screen = HomePage(self)
        else:
            screen = InitWindow(self)

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        screen.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        screen.show()


def gset(event = None):
    #root.grab_set_global()
    pass

videoScreen = None
loginScreen = None
videoScreen1 = None
loginScreen1 = None
F1 = None
F2 = None

nvpass_auth = False
nvpass_new = False

i = 0
def init_auth(NextWindow = None):
    global i , AuthStatus , videoScreen , loginScreen , nvpass_auth, F1
    print(i, AuthStatus, nvpass_auth)

    if i == 0 and not nvpass_auth:
        # NV Password Verification Screen
        def verify_password(event = None):
            global nvpass_auth
            PASS1 = E_nvpass.get()
            path = getZeroVDevice()['devicePath'] + default_path
            file = open(path + "/nvconfig", 'rb')
            actual_pass = fernet.decrypt(file.read()).decode()
            file.close()
            if PASS1 == actual_pass:
                nvpass_auth = True
            pass

        F1 = Frame(root, bg = 'white')
        #F1.pack(side="top", fill="both", expand=True)
        F1.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
        #F1.tkraise()
        L = Label(F1, text = "Enter NatiVault Password", bg = 'white', fg = 'red', font=('arial', 14, 'bold'))
        L.pack(padx=20, pady=20)
        E_nvpass = ttk.Entry(F1, show = '*')
        E_nvpass.pack(padx=10, pady=20)
        E_nvpass.focus()
        B_login = ttk.Button(F1, text = "Login", command = verify_password)
        B_login.pack(padx=20, pady=20)
        L = Label(F1, text = "After Clicking Login,\nOn next screen, keep your face steady. You should be identified by 'NV_USER'.\nBlink 4 times within 20 seconds to login, else timeout.", bg = 'white')
        L.pack(padx = 5, pady = 5)
        print("Screen Created")

        i = 1
        pass
    
    if i == 1 and nvpass_auth:
        F1.place_forget()
        del F1
        videoScreen = Frame(root)
        #videoScreen.pack(side="top", fill="both", expand=True)
        videoScreen.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
        loginScreen = VideoAuthPage(videoScreen)
        loginScreen.place(in_=videoScreen, x=0, y=0, relwidth=1, relheight=1)
        loginScreen.show()
        i = 2

    if AuthStatus:
        videoScreen.place_forget()
        if i == 2:
            loginScreen.place_forget()
            loginScreen.releaseResourses()
            del loginScreen
            i = 2
        if not NextWindow == None:
            main = NextWindow(root)
            main.pack(side="top", fill="both", expand=True)
    
    if not AuthStatus and nvpass_auth:
        try:
            F1.place_forget()
            del F1
            print("Forgot F1")
        except Exception as e:
            print(e)
        AuthStatus, diff = loginScreen.displayVideo()
        if diff > TIMEOUT and NextWindow == MainView:
            root.destroy()
        root.after(1, lambda: init_auth(NextWindow = NextWindow))

    else:
        root.after(1, lambda: init_auth(NextWindow = NextWindow))

i = 0
def new_auth():
    global i , accountCreated , videoScreen1 , loginScreen1 , nvpass_new

    if i == 0 and not nvpass_new:
        # NV Password Creation Screen
        def activate_button(event = None):
            PASS1 = E_nvpass1.get()
            PASS2 = E_nvpass2.get()
            if PASS1 == PASS2 and len(PASS1) >= 8:
                B_login.config(state = NORMAL)
                L_signup.config(text = "After Clicking Register,\nKeep your face steady and capture your Face identified by red box.\nMake sure the lighting is proper and face image is clear.")
            else:
                B_login.config(state = DISABLED)
                L_signup.config(text = "Either Passwords Do not match or\nPassword Length is less than 8 characters.\nTry again.")

        def verify_password(event = None):
            global nvpass_new
            PASS1 = E_nvpass1.get()
            path = getZeroVDevice()['devicePath'] + default_path
            os.makedirs(path)
            file = open(path + "/nvconfig", 'wb')
            file.write(fernet.encrypt(PASS1.encode()))
            file.close()
            nvpass_new = True
            
            pass

        F1 = Frame(root, bg = 'white')
        #F1.pack(side="top", fill="both", expand=True)
        F1.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
        #F1.tkraise()
        L = Label(F1, text = "Create NatiVault Account", bg = 'white', fg = 'red', font=('arial', 14, 'bold'))
        L.pack(padx=20, pady=20)
        L = Label(F1, text = "Enter Password", bg = 'white')
        L.pack(padx = 10, pady = 2)
        E_nvpass1 = ttk.Entry(F1, show = '*')
        E_nvpass1.pack(padx=10, pady=5)
        E_nvpass1.bind('<KeyRelease>', activate_button)
        L = Label(F1, text = "Re-Enter Password", bg = 'white')
        L.pack(padx = 10, pady = 2)
        E_nvpass2 = ttk.Entry(F1, show = '*')
        E_nvpass2.pack(padx=10, pady=5)
        E_nvpass2.bind('<KeyRelease>', activate_button)
        E_nvpass1.focus()
        B_login = ttk.Button(F1, text = "Register", state = DISABLED, command = verify_password)
        B_login.pack(padx=20, pady=20)
        L_signup = Label(F1, text = "After Clicking Register,\nKeep your face steady and capture your Face identified by red box.\nMake sure the lighting is proper and face image is clear.", bg = 'white')
        L_signup.pack(padx = 10, pady = 2)
        print("Screen Created")

        i = 1
        pass

    if i == 1 and nvpass_new:
        try:
            F1.place_forget()
            del F1
        except Exception:
            pass
        videoScreen1 = Frame(root)
        videoScreen1.pack(side="top", fill="both", expand=True)
        loginScreen1 = VideoNewPage(videoScreen1)
        loginScreen1.place(in_=videoScreen1, x=0, y=0, relwidth=1, relheight=1)
        loginScreen1.show()
        i = 2

    if accountCreated:
        videoScreen1.pack_forget()
        if i == 2:
            loginScreen1.place_forget()
            loginScreen1.releaseResourses()
            del loginScreen1
            i = 2
        main = MainView(root)
        main.pack(side="top", fill="both", expand=True)
    
    if not accountCreated and nvpass_new:
        accountCreated = loginScreen1.displayNewVideo()
        root.after(1, new_auth)

    else:
        root.after(1, new_auth)


if __name__ == "__main__":
    root = Tk(className = "NatiVault")
    root.title("NatiVault - 1.0.1")
    try:
        img = PhotoImage(file='/home/{}/.config/NV/NV.png'.format(getpass.getuser()))
        root.tk.call('wm', 'iconphoto', root._w, img)
    except Exception as e:
        print(e)
        pass
    root.config(bg = 'white')
    #main = MainView(root)
    #main.pack(side="top", fill="both", expand=True)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width/2) - (600/2))
    y = int((screen_height/2) - (350/2))
    root.geometry("600x350+"+str(x)+"+"+str(y))
    root.resizable(height = FALSE, width = FALSE)

    root.after(1000, gset)
    root.protocol("ICONIC", lambda: print("ICONIFY"))
    root.bind("<Unmap>", lambda x: print("ICONIFY"))
    


    #----------------Video Login Process-------------------#
    configuration = Configuration(config_dir = CONFIG_DIR, initial_config = INITIAL_CONFIG)
    if configuration.is_configuration():
        AuthStatus = False
        accountCreated = False
        root.after(1000, lambda: init_auth(NextWindow = MainView))
        #root.after(5000, init_auth)
        #root.after(5000, new_auth)

    else:
        accountCreated = False
        root.after(1000, new_auth)






    try:
        import pyi_splash
        pyi_splash.update_text("NV UI Loaded...")
        pyi_splash.close()
    except:
        pass
        
    root.mainloop()
