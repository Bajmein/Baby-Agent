import customtkinter as ctk
import MetaTrader5 as mt5


class FloatSpinbox(ctk.CTkFrame):
    def __init__(self, *args,
                 width=100,
                 height=32,
                 step_size=0.0,
                 command=None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))

        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.subtract_button = ctk.CTkButton(self, text="-", width=height - 6, height=height - 6,
                                             command=self.subtract_button_callback, fg_color='#003c66',
                                             hover_color='#000f1a')
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = ctk.CTkEntry(self, width=width - (2 * height), height=height - 6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = ctk.CTkButton(self, text="+", width=height - 6, height=height - 6,
                                        command=self.add_button_callback, fg_color='#003c66',
                                        hover_color='#000f1a')
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.insert(0, "0.0")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) + self.step_size
            value = round(value, 5)
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) - self.step_size
            value = round(value, 5)
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self):
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))


class BabyAgent:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry('350x480')
        self.root.title('Baby Agent')
        self.root.resizable(False, False)

        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(pady=30, padx=50, fill="both", expand=True)

        self.title_font = ctk.CTkFont(family="Tourney", size=25, weight='bold')
        self.label = ctk.CTkLabel(master=self.frame, text="Login", font=self.title_font)
        self.label.pack(pady=(60, 0), padx=10)

        self.cuenta = ctk.CTkEntry(master=self.frame, placeholder_text='Cuenta')
        self.cuenta.pack(pady=(60, 12), padx=10)
        self.password = ctk.CTkEntry(master=self.frame, placeholder_text='password', show="*")
        self.password.pack(pady=12, padx=10)
        self.server = ctk.CTkEntry(master=self.frame, placeholder_text='server')
        self.server.pack(pady=12, padx=10)

        self.boton = ctk.CTkButton(master=self.frame, text="Login", command=self.login)
        self.boton.pack(pady=12, padx=10)

        self.par = 'EURUSD'

        self.porcentaje_riesgo = None
        self.stop_loss = None
        self.font = None
        self.btn_font = None
        self.buy = None
        self.sell = None
        self.texto = None
        self.reset = None
        self.cerrar_sesion = None

    def login_gui(self):
        self.frame.destroy()
        self.root.geometry('350x480')
        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(pady=30, padx=50, fill="both", expand=True)

        self.title_font = ctk.CTkFont(family="Tourney", size=25, weight='bold')
        self.label = ctk.CTkLabel(master=self.frame, text="Login", font=self.title_font)
        self.label.pack(pady=(60, 0), padx=10)

        self.cuenta = ctk.CTkEntry(master=self.frame, placeholder_text='Cuenta')
        self.cuenta.pack(pady=(60, 12), padx=10)
        self.password = ctk.CTkEntry(master=self.frame, placeholder_text='password', show="*")
        self.password.pack(pady=12, padx=10)
        self.server = ctk.CTkEntry(master=self.frame, placeholder_text='server')
        self.server.pack(pady=12, padx=10)

        self.boton = ctk.CTkButton(master=self.frame, text="Login", command=self.login)
        self.boton.pack(pady=12, padx=10)

    def reset_boton(self):
        self.buy.configure(state='normal')
        self.sell.configure(state='normal')
        self.reset.configure(state='disabled')

    def destroy(self):
        self.cuenta.destroy()
        self.password.destroy()
        self.server.destroy()
        self.boton.destroy()
        self.label.destroy()

    def op_buy(self):
        try:
            porcentaje_riesgo = float(self.porcentaje_riesgo.get())
            stop_loss = self.stop_loss.get()
            balance_cuenta = mt5.account_info().balance
            tamano_posicion = balance_cuenta * porcentaje_riesgo
            relacion_beneficio = 2
            lote = 100000
            precio_euro = mt5.symbol_info_tick(self.par).ask
            lot = round((tamano_posicion / (precio_euro - stop_loss) / lote), 2)
            take_profit = round(precio_euro + ((precio_euro - stop_loss) * relacion_beneficio), 5)
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.par,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": precio_euro,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 20,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            resultado = mt5.order_send(request)
            if resultado.retcode != mt5.TRADE_RETCODE_DONE:
                self.texto.configure(text=f'¡Error al enviar la orden: {resultado.comment}!')
            else:
                self.buy.configure(state='disabled')
                self.sell.configure(state='disabled')
                self.reset.configure(state='normal')
                self.texto.configure(text='¡Orden de compra enviada correctamente!')
            return resultado
        except TypeError:
            self.texto.configure(text="Stop Loss inválido")
            return
        except ValueError:
            self.texto.configure(text="Porcentaje de riesgo inválido")
            return
        except UnboundLocalError:
            return

    def op_sell(self):
        try:
            porcentaje_riesgo = float(self.porcentaje_riesgo.get())
            stop_loss = self.stop_loss.get()
            balance_cuenta = mt5.account_info().balance
            tamano_posicion = balance_cuenta * porcentaje_riesgo
            lote = 100000
            relacion_beneficio = 2
            precio_euro = mt5.symbol_info_tick(self.par).bid
            lot = round((tamano_posicion / (stop_loss - precio_euro) / lote), 2)
            take_profit = precio_euro - ((stop_loss - precio_euro) * relacion_beneficio)
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.par,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": precio_euro,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 20,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            resultado = mt5.order_send(request)
            if resultado.retcode != mt5.TRADE_RETCODE_DONE:
                self.texto.configure(text=f'¡Error al enviar la orden: {resultado.comment}!')
            else:
                self.buy.configure(state='disabled')
                self.sell.configure(state='disabled')
                self.reset.configure(state='normal')
                self.texto.configure(text='¡Orden de venta enviada correctamente!')
            return resultado
        except TypeError:
            self.texto.configure(text="Stop Loss inválido")
            return
        except ValueError:
            self.texto.configure(text="Porcentaje de riesgo inválido")
            return
        except UnboundLocalError:
            return

    def operational_gui(self):
        self.frame.pack(pady=30, padx=20, fill="both", expand=True)
        self.title_font = ctk.CTkFont(family="Tourney", size=25, weight='bold')
        self.label = ctk.CTkLabel(master=self.frame, text="Operación", font=self.title_font)
        self.label.pack(pady=30, padx=10)
        self.root.geometry("350x550")
        self.porcentaje_riesgo = ctk.CTkEntry(master=self.frame, placeholder_text='Porcentaje de riesgo', width=152,
                                              height=35)
        self.porcentaje_riesgo.pack(pady=5, padx=20)
        self.stop_loss = FloatSpinbox(self.frame, width=150, step_size=0.00001)
        self.stop_loss.pack(pady=15, padx=20)
        self.stop_loss.set(0.0)
        self.font = ctk.CTkFont(size=14)
        self.btn_font = ctk.CTkFont(weight='bold')
        self.buy = ctk.CTkButton(master=self.frame, text="Buy", fg_color="#b38600", hover_color="#664d00", width=152,
                                 height=35, command=self.op_buy, font=self.btn_font)
        self.buy.pack(pady=10, padx=20)
        self.sell = ctk.CTkButton(master=self.frame, text="Sell", fg_color="#4d0066", hover_color="#39004d", width=152,
                                  height=35, command=self.op_sell, font=self.btn_font)
        self.sell.pack(pady=10, padx=20)
        self.texto = ctk.CTkLabel(master=self.frame, text='', font=self.font)
        self.texto.pack(pady=15, padx=20)

        self.reset = ctk.CTkButton(master=self.frame, text='Activar botones', fg_color='#000f1a', hover_color='#003c66',
                                   width=120, height=35, state='disabled', command=self.reset_boton, font=self.btn_font)
        self.reset.pack(pady=10, padx=20)
        self.cerrar_sesion = ctk.CTkButton(master=self.frame, text='Cerrar sesión', command=self.login_gui,
                                           fg_color="transparent", hover_color='#141514')
        self.cerrar_sesion.pack(pady=10, padx=20)

    def login(self):
        cuenta = int(self.cuenta.get())
        password = self.password.get()
        server = self.server.get()
        self.destroy()
        mt5.initialize()
        mt5.login(cuenta, password, server)
        self.operational_gui()


if __name__ == '__main__':
    app = BabyAgent()
    app.root.mainloop()
