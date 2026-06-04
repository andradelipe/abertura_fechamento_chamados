import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import threading

# Carregar CSV
def load_hardware_data():
    try:
        return pd.read_csv("alm_hardware.csv", low_memory=False, encoding="latin1")
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        return pd.DataFrame()

class ModernButton(tk.Button):
    def __init__(self, master, text, command, bg_color="#2196F3", **kwargs):
        super().__init__(master, text=text, command=command, 
                        bg=bg_color, fg="white", font=("Segoe UI", 10, "bold"),
                        relief="flat", cursor="hand2", padx=20, pady=8, **kwargs)
        self.bind("<Enter>", lambda e: self.config(bg=self.darken_color(bg_color)))
        self.bind("<Leave>", lambda e: self.config(bg=bg_color))
    
    def darken_color(self, color):
        # Simplificado - retorna cor mais escura
        return "#1976D2" if color == "#2196F3" else "#388E3C" if color == "#4CAF50" else "#D32F2F"

class RegistroAtividadesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📒 Registro de Atividades")
        self.root.geometry("1400x800")
        self.root.configure(bg="#1e1e1e")
        
        # Estado
        self.atividades = []
        self.df_host = load_hardware_data()
        self.current_form_data = {}
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#1e1e1e", tabmargins=0)
        style.configure("TNotebook.Tab", background="#2d2d2d", foreground="white", padding=[20, 5], font=("Segoe UI", 11))
        style.map("TNotebook.Tab", background=[("selected", "#2196F3")], foreground=[("selected", "white")])
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabelframe", background="#2d2d2d", foreground="white", font=("Segoe UI", 10))
        style.configure("TLabelframe.Label", background="#2d2d2d", foreground="white")
        
        # Criar abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.criar_aba_cadastro()
        self.criar_aba_registros()
        self.criar_aba_substituicoes()
        self.criar_aba_host()
        self.criar_aba_resumo()
    
    def criar_aba_cadastro(self):
        self.aba_cadastro = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_cadastro, text="📌 Cadastro")
        
        # Container principal
        main_container = ttk.Frame(self.aba_cadastro)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_container, text="REGISTRO DE ATIVIDADES", font=("Segoe UI", 18, "bold"), 
                bg="#1e1e1e", fg="#2196F3").pack(pady=10)
        
        # Frame do formulário (centralizado)
        form_frame = ttk.Frame(main_container)
        form_frame.pack(anchor="center", pady=20)
        
        # Dados principais
        main_form = ttk.LabelFrame(form_frame, text="Dados da Atividade", padding=15)
        main_form.pack(fill="x", pady=10)
        
        # Grid para campos principais
        tk.Label(main_form, text="Descrição da Falha:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.txt_descricao = tk.Text(main_form, height=4, width=50, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 10))
        self.txt_descricao.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(main_form, text="Ação Corretiva:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.txt_acao = tk.Text(main_form, height=4, width=50, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 10))
        self.txt_acao.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(main_form, text="Etiqueta Stellantis (CI):", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.etiqueta_var = tk.StringVar()
        self.etiqueta_var.trace('w', lambda *args: self.buscar_etiqueta())
        tk.Entry(main_form, textvariable=self.etiqueta_var, width=50, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 10)).grid(row=2, column=1, pady=5, padx=10)
        self.label_status = tk.Label(main_form, text="", bg="#2d2d2d", font=("Segoe UI", 9))
        self.label_status.grid(row=2, column=2, pady=5, padx=5)
        
        tk.Label(main_form, text="Serial:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.serial_var = tk.StringVar()
        tk.Entry(main_form, textvariable=self.serial_var, width=50, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 10)).grid(row=3, column=1, pady=5, padx=10)
        
        tk.Label(main_form, text="Galpão:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.galpao_var = tk.StringVar()
        tk.Entry(main_form, textvariable=self.galpao_var, width=50, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 10)).grid(row=4, column=1, pady=5, padx=10)
        
        tk.Label(main_form, text="Room/Setor:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=5, column=0, sticky="w", pady=5, padx=5)
        self.room_var = tk.StringVar()
        tk.Entry(main_form, textvariable=self.room_var, width=50, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 10)).grid(row=5, column=1, pady=5, padx=10)
        
        tk.Label(main_form, text="Solicitante:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=6, column=0, sticky="w", pady=5, padx=5)
        self.solicitante_var = tk.StringVar()
        tk.Entry(main_form, textvariable=self.solicitante_var, width=50, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 10)).grid(row=6, column=1, pady=5, padx=10)
        
        # Checkbox substituição
        self.subs_var = tk.BooleanVar()
        cb_subs = tk.Checkbutton(main_form, text="✓ Equipamento Substituído", variable=self.subs_var, 
                                 command=self.toggle_substituicao, bg="#2d2d2d", fg="white", 
                                 selectcolor="#2d2d2d", font=("Segoe UI", 10, "bold"))
        cb_subs.grid(row=7, column=0, columnspan=2, pady=15)
        
        # Frame para equipamentos (lado a lado)
        self.frame_equipamentos = ttk.Frame(form_frame)
        
        # Botão Registrar
        ModernButton(main_form, text="🚀 REGISTRAR ATIVIDADE", command=self.registrar, bg_color="#4CAF50").grid(row=8, column=0, columnspan=2, pady=20)
    
    def toggle_substituicao(self):
        if self.subs_var.get():
            # Limpar frame
            for widget in self.frame_equipamentos.winfo_children():
                widget.destroy()
            
            # Frame para lado a lado
            container = ttk.Frame(self.frame_equipamentos)
            container.pack(fill="x", expand=True)
            
            # Instalado (esquerda)
            frame_inst = ttk.LabelFrame(container, text="➡️ EQUIPAMENTO INSTALADO", padding=15)
            frame_inst.pack(side="left", fill="both", expand=True, padx=5)
            
            # Campos Instalado
            labels_inst = ["Serial:", "IP:", "Item de Configuração:", "Modelo:", "Floor:", "Room:", "Aplicação:"]
            self.inst_vars = {}
            
            for i, label in enumerate(labels_inst):
                tk.Label(frame_inst, text=label, bg="#2d2d2d", fg="white", font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=3, padx=5)
                var = tk.StringVar()
                entry = tk.Entry(frame_inst, textvariable=var, width=30, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 9))
                entry.grid(row=i, column=1, pady=3, padx=5)
                self.inst_vars[label] = var
            
            # Valores padrão
            self.inst_vars["Estado:"] = tk.StringVar(value="Em uso")
            self.inst_vars["Subestado:"] = tk.StringVar(value="Disponível")
            self.inst_vars["Função:"] = tk.StringVar(value="Compartilhado")
            
            tk.Label(frame_inst, text="Estado:", bg="#2d2d2d", fg="white", font=("Segoe UI", 9)).grid(row=len(labels_inst), column=0, sticky="w", pady=3, padx=5)
            tk.Entry(frame_inst, textvariable=self.inst_vars["Estado:"], width=30, bg="#3c3c3c", fg="white", font=("Segoe UI", 9)).grid(row=len(labels_inst), column=1, pady=3, padx=5)
            
            tk.Label(frame_inst, text="Subestado:", bg="#2d2d2d", fg="white", font=("Segoe UI", 9)).grid(row=len(labels_inst)+1, column=0, sticky="w", pady=3, padx=5)
            tk.Entry(frame_inst, textvariable=self.inst_vars["Subestado:"], width=30, bg="#3c3c3c", fg="white", font=("Segoe UI", 9)).grid(row=len(labels_inst)+1, column=1, pady=3, padx=5)
            
            tk.Label(frame_inst, text="Função:", bg="#2d2d2d", fg="white", font=("Segoe UI", 9)).grid(row=len(labels_inst)+2, column=0, sticky="w", pady=3, padx=5)
            tk.Entry(frame_inst, textvariable=self.inst_vars["Função:"], width=30, bg="#3c3c3c", fg="white", font=("Segoe UI", 9)).grid(row=len(labels_inst)+2, column=1, pady=3, padx=5)
            
            # Recolhido (direita)
            frame_rec = ttk.LabelFrame(container, text="⬅️ EQUIPAMENTO RECOLHIDO", padding=15)
            frame_rec.pack(side="right", fill="both", expand=True, padx=5)
            
            labels_rec = ["Modelo:", "Floor:", "Room:", "Estado:", "Subestado:"]
            self.rec_vars = {}
            default_rec = {"Floor:": "Galpão 01", "Room:": "Sala 12 (Laboratório Atos)", "Estado:": "Em estoque", "Subestado:": "Recuperação pendente"}
            
            for i, label in enumerate(labels_rec):
                tk.Label(frame_rec, text=label, bg="#2d2d2d", fg="white", font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=3, padx=5)
                var = tk.StringVar(value=default_rec.get(label, ""))
                tk.Entry(frame_rec, textvariable=var, width=30, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 9)).grid(row=i, column=1, pady=3, padx=5)
                self.rec_vars[label] = var
            
            self.frame_equipamentos.pack(fill="x", pady=10)
        else:
            self.frame_equipamentos.pack_forget()
    
    def buscar_etiqueta(self):
        etiqueta = self.etiqueta_var.get().strip()
        if not etiqueta or self.df_host.empty:
            self.label_status.config(text="", bg="#2d2d2d")
            return
        
        match = self.df_host[self.df_host['ci'].astype(str).str.strip().str.upper() == etiqueta.upper()]
        if not match.empty:
            row = match.iloc[0]
            self.serial_var.set(str(row['serial_number']) if pd.notna(row['serial_number']) else "")
            self.galpao_var.set(str(row['u_floor']) if pd.notna(row['u_floor']) else "")
            self.room_var.set(str(row['u_room']) if pd.notna(row['u_room']) else "")
            modelo = str(row['display_name']) if pd.notna(row['display_name']) else ""
            
            if hasattr(self, 'rec_vars') and 'Modelo:' in self.rec_vars:
                self.rec_vars['Modelo:'].set(modelo)
            if hasattr(self, 'inst_vars') and 'Floor:' in self.inst_vars:
                self.inst_vars['Floor:'].set(str(row['u_floor']) if pd.notna(row['u_floor']) else "")
            if hasattr(self, 'inst_vars') and 'Room:' in self.inst_vars:
                self.inst_vars['Room:'].set(str(row['u_room']) if pd.notna(row['u_room']) else "")
            
            self.label_status.config(text="✅ Host OK!", fg="lightgreen", bg="#2d2d2d")
        else:
            self.label_status.config(text="⚠️ Não encontrado", fg="orange", bg="#2d2d2d")
    
    def registrar(self):
        atividade = {
            "Descrição da falha": self.txt_descricao.get("1.0", tk.END).strip(),
            "Ação corretiva": self.txt_acao.get("1.0", tk.END).strip(),
            "Etiqueta": self.etiqueta_var.get(),
            "Serial": self.serial_var.get(),
            "Galpão": self.galpao_var.get(),
            "Room/Setor": self.room_var.get(),
            "Solicitante": self.solicitante_var.get(),
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Equipamento substituído": self.subs_var.get()
        }
        
        if self.subs_var.get() and hasattr(self, 'inst_vars') and hasattr(self, 'rec_vars'):
            atividade.update({
                "Eq Serial": self.inst_vars.get("Serial:", tk.StringVar()).get(),
                "Eq IP": self.inst_vars.get("IP:", tk.StringVar()).get(),
                "Eq Item Config": self.inst_vars.get("Item de Configuração:", tk.StringVar()).get(),
                "Eq Modelo": self.inst_vars.get("Modelo:", tk.StringVar()).get(),
                "Eq Florr": self.inst_vars.get("Floor:", tk.StringVar()).get(),
                "Eq Room": self.inst_vars.get("Room:", tk.StringVar()).get(),
                "Eq Aplicação": self.inst_vars.get("Aplicação:", tk.StringVar()).get(),
                "Eq Estado": self.inst_vars.get("Estado:", tk.StringVar()).get(),
                "Eq Subestado": self.inst_vars.get("Subestado:", tk.StringVar()).get(),
                "Eq Função": self.inst_vars.get("Função:", tk.StringVar()).get(),
                "Rec Modelo": self.rec_vars.get("Modelo:", tk.StringVar()).get(),
                "Rec Florr": self.rec_vars.get("Floor:", tk.StringVar()).get(),
                "Rec Room": self.rec_vars.get("Room:", tk.StringVar()).get(),
                "Rec Estado": self.rec_vars.get("Estado:", tk.StringVar()).get(),
                "Rec Subestado": self.rec_vars.get("Subestado:", tk.StringVar()).get()
            })
        
        self.atividades.append(atividade)
        
        # Limpar formulário
        self.txt_descricao.delete("1.0", tk.END)
        self.txt_acao.delete("1.0", tk.END)
        self.etiqueta_var.set("")
        self.serial_var.set("")
        self.galpao_var.set("")
        self.room_var.set("")
        self.solicitante_var.set("")
        self.subs_var.set(False)
        
        self.atualizar_registros()
        self.atualizar_substituicoes()
        self.atualizar_resumo()
        
        messagebox.showinfo("Sucesso", "✅ Atividade registrada com sucesso!")
    
    def criar_aba_registros(self):
        self.aba_registros = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_registros, text="📋 Registros")
        
        # Frame principal
        main = ttk.Frame(self.aba_registros)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview
        frame_tree = ttk.Frame(main)
        frame_tree.pack(fill="both", expand=True)
        
        scroll_y = ttk.Scrollbar(frame_tree, orient="vertical")
        scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal")
        
        self.tree = ttk.Treeview(frame_tree, columns=("ID", "Falha", "Setor", "Data", "Solicitante"), 
                                  show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Falha", text="Descrição da Falha")
        self.tree.heading("Setor", text="Setor")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Solicitante", text="Solicitante")
        
        self.tree.column("ID", width=50)
        self.tree.column("Falha", width=400)
        self.tree.column("Setor", width=150)
        self.tree.column("Data", width=120)
        self.tree.column("Solicitante", width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        # Botões
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=10)
        
        ModernButton(btn_frame, text="🔍 Ver Detalhes", command=self.ver_detalhes, bg_color="#2196F3").pack(side="left", padx=5)
        ModernButton(btn_frame, text="🗑️ Apagar", command=self.apagar_registro, bg_color="#f44336").pack(side="left", padx=5)
        ModernButton(btn_frame, text="⚠️ Limpar Todos", command=self.limpar_todos, bg_color="#FF9800").pack(side="left", padx=5)
        ModernButton(btn_frame, text="📥 Exportar CSV", command=self.exportar_csv, bg_color="#4CAF50").pack(side="left", padx=5)
    
    def atualizar_registros(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, a in enumerate(self.atividades):
            self.tree.insert("", "end", values=(
                i+1,
                a.get("Descrição da falha", "")[:60],
                a.get("Room/Setor", ""),
                a.get("Data", ""),
                a.get("Solicitante", "")
            ))
    
    def ver_detalhes(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um registro!")
            return
        item = self.tree.item(selecionado[0])
        idx = int(item['values'][0]) - 1
        atividade = self.atividades[idx]
        detalhes = "\n".join([f"{k}: {v}" for k, v in atividade.items()])
        
        # Janela de detalhes
        detail_win = tk.Toplevel(self.root)
        detail_win.title("Detalhes do Registro")
        detail_win.geometry("600x500")
        detail_win.configure(bg="#1e1e1e")
        
        text = tk.Text(detail_win, wrap="word", bg="#2d2d2d", fg="white", font=("Consolas", 10))
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", detalhes)
        text.config(state="disabled")
    
    def apagar_registro(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um registro!")
            return
        if messagebox.askyesno("Confirmar", "Apagar este registro?"):
            item = self.tree.item(selecionado[0])
            idx = int(item['values'][0]) - 1
            self.atividades.pop(idx)
            self.atualizar_registros()
            self.atualizar_substituicoes()
    
    def limpar_todos(self):
        if messagebox.askyesno("Confirmar", "Apagar TODOS os registros?"):
            self.atividades.clear()
            self.atualizar_registros()
            self.atualizar_substituicoes()
    
    def exportar_csv(self):
        if not self.atividades:
            messagebox.showwarning("Aviso", "Nenhum registro para exportar!")
            return
        df = pd.DataFrame(self.atividades)
        df.to_csv("registros_atividades.csv", index=False, encoding="utf-8-sig")
        messagebox.showinfo("Sucesso", "Exportado para registros_atividades.csv")
    
    def criar_aba_substituicoes(self):
        self.aba_subs = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_subs, text="🔄 Substituições")
        
        # Treeview para substituições
        frame_tree = ttk.Frame(self.aba_subs)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_tree, orient="vertical")
        scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal")
        
        self.tree_subs = ttk.Treeview(frame_tree, columns=("ID", "Falha", "Serial Instalado", "Modelo Recolhido", "Data"), 
                                       show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree_subs.yview)
        scroll_x.config(command=self.tree_subs.xview)
        
        self.tree_subs.heading("ID", text="ID")
        self.tree_subs.heading("Falha", text="Descrição da Falha")
        self.tree_subs.heading("Serial Instalado", text="Serial Instalado")
        self.tree_subs.heading("Modelo Recolhido", text="Modelo Recolhido")
        self.tree_subs.heading("Data", text="Data")
        
        self.tree_subs.column("ID", width=50)
        self.tree_subs.column("Falha", width=400)
        self.tree_subs.column("Serial Instalado", width=150)
        self.tree_subs.column("Modelo Recolhido", width=150)
        self.tree_subs.column("Data", width=120)
        
        self.tree_subs.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
    
    def atualizar_substituicoes(self):
        for i in self.tree_subs.get_children():
            self.tree_subs.delete(i)
        subs = [a for a in self.atividades if a.get("Equipamento substituído") == True]
        for i, sub in enumerate(subs, 1):
            self.tree_subs.insert("", "end", values=(
                i,
                sub.get("Descrição da falha", "")[:50],
                sub.get("Eq Serial", ""),
                sub.get("Rec Modelo", ""),
                sub.get("Data", "")
            ))
    
    def criar_aba_host(self):
        self.aba_host = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_host, text="🌐 Host")
        
        # Frame superior com total e busca
        top_frame = ttk.Frame(self.aba_host)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_label = tk.Label(top_frame, text=f"Total: {len(self.df_host)} equipamentos", 
                                   bg="#1e1e1e", fg="#2196F3", font=("Segoe UI", 12, "bold"))
        self.total_label.pack(side="left", padx=10)
        
        # Busca em tempo real
        busca_frame = ttk.Frame(top_frame)
        busca_frame.pack(side="right")
        
        tk.Label(busca_frame, text="🔍 Buscar:", bg="#1e1e1e", fg="white", font=("Segoe UI", 10)).pack(side="left", padx=5)
        self.busca_host_var = tk.StringVar()
        self.busca_host_var.trace('w', lambda *args: self.filtrar_host())
        tk.Entry(busca_frame, textvariable=self.busca_host_var, width=30, bg="#3c3c3c", fg="white", 
                insertbackground="white", font=("Segoe UI", 10)).pack(side="left", padx=5)
        
        # Treeview Host
        frame_tree = ttk.Frame(self.aba_host)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_tree, orient="vertical")
        scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal")
        
        self.tree_host = ttk.Treeview(frame_tree, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree_host.yview)
        scroll_x.config(command=self.tree_host.xview)
        
        self.tree_host.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        # Carregar dados
        self.carregar_host()
    
    def carregar_host(self, busca=""):
        for i in self.tree_host.get_children():
            self.tree_host.delete(i)
        
        if self.df_host.empty:
            return
        
        # Filtrar
        if busca:
            mask = (
                self.df_host['serial_number'].astype(str).str.contains(busca, case=False, na=False) |
                self.df_host['asset_tag'].astype(str).str.contains(busca, case=False, na=False) |
                self.df_host['ci'].astype(str).str.contains(busca, case=False, na=False)
            )
            df_filtrado = self.df_host[mask]
            self.total_label.config(text=f"Resultados: {len(df_filtrado)} / {len(self.df_host)} equipamentos")
        else:
            df_filtrado = self.df_host.head(100)
            self.total_label.config(text=f"Mostrando 100 / {len(self.df_host)} equipamentos")
        
        # Colunas
        colunas = ['ci', 'asset_tag', 'serial_number', 'display_name', 'u_floor', 'u_room']
        colunas_existentes = [c for c in colunas if c in df_filtrado.columns]
        
        # Renomear para exibição
        nomes_exibicao = {
            'ci': 'CI',
            'asset_tag': 'Asset Tag',
            'serial_number': 'Serial Number',
            'display_name': 'Modelo',
            'u_floor': 'Floor',
            'u_room': 'Room'
        }
        
        self.tree_host["columns"] = colunas_existentes
        self.tree_host["show"] = "headings"
        
        for col in colunas_existentes:
            self.tree_host.heading(col, text=nomes_exibicao.get(col, col))
            self.tree_host.column(col, width=150)
        
        for _, row in df_filtrado.iterrows():
            valores = [str(row[col]) if pd.notna(row[col]) else "" for col in colunas_existentes]
            self.tree_host.insert("", "end", values=valores)
    
    def filtrar_host(self):
        self.carregar_host(self.busca_host_var.get())
    
    def criar_aba_resumo(self):
        self.aba_resumo = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_resumo, text="📄 Resumo Atual")
        
        # Frame com botões
        btn_frame = ttk.Frame(self.aba_resumo)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ModernButton(btn_frame, text="📋 Copiar Tudo", command=self.copiar_resumo, bg_color="#2196F3").pack(side="left", padx=5)
        ModernButton(btn_frame, text="🔄 Atualizar", command=self.atualizar_resumo, bg_color="#4CAF50").pack(side="left", padx=5)
        
        # Texto editável e selecionável
        self.resumo_text = tk.Text(self.aba_resumo, wrap="word", bg="#2d2d2d", fg="white", 
                                   insertbackground="white", font=("Consolas", 10), 
                                   selectbackground="#2196F3", selectforeground="white")
        self.resumo_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind para atualização automática
        self.atualizar_resumo()
        
        # Atualizar quando campos mudarem
        self.after_id = None
        self.schedule_resumo_update()
    
    def schedule_resumo_update(self):
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(500, self.atualizar_resumo)
    
    def atualizar_resumo(self):
        if not hasattr(self, 'resumo_text'):
            return
        
        self.resumo_text.delete("1.0", tk.END)
        
        descricao = self.txt_descricao.get("1.0", tk.END).strip() if hasattr(self, 'txt_descricao') else ""
        acao = self.txt_acao.get("1.0", tk.END).strip() if hasattr(self, 'txt_acao') else ""
        etiqueta = self.etiqueta_var.get() if hasattr(self, 'etiqueta_var') else ""
        serial = self.serial_var.get() if hasattr(self, 'serial_var') else ""
        galpao = self.galpao_var.get() if hasattr(self, 'galpao_var') else ""
        room = self.room_var.get() if hasattr(self, 'room_var') else ""
        solicitante = self.solicitante_var.get() if hasattr(self, 'solicitante_var') else ""
        
        resumo = f"""╔══════════════════════════════════════════════════════════════════╗
║                           ABERTURA                                      ║
╠════════════════════════════════════════════════════════════════════════╣
║ DESCRIÇÃO:                                                              ║
║ {descricao if descricao else '—'}{' ' * (60 - len(descricao if descricao else '—'))}║
║                                                                         ║
║ SETOR: {room if room else '—'}{' ' * (55 - len(room if room else '—'))}║
║                                                                         ║
║ GALPÃO e Coluna: {galpao if galpao else '—'}{' ' * (46 - len(galpao if galpao else '—'))}║
║                                                                         ║
║ CELULAR: (31)9 95426967{' ' * 37}║
║                                                                         ║
║ ETIQUETA STELLANTIS: {etiqueta if etiqueta else '—'}{' ' * (45 - len(etiqueta if etiqueta else '—'))}║
║                                                                         ║
║ SERIAL NUMBER: {serial if serial else '—'}{' ' * (48 - len(serial if serial else '—'))}║
║                                                                         ║
║ SOLICITANTE: {solicitante if solicitante else '—'}{' ' * (51 - len(solicitante if solicitante else '—'))}║
║                                                                         ║
╠════════════════════════════════════════════════════════════════════════╣
║                           ENCERRAMENTO                                 ║
╠════════════════════════════════════════════════════════════════════════╣
║ FALHA:                                                                  ║
║ {descricao if descricao else '—'}{' ' * (60 - len(descricao if descricao else '—'))}║
║                                                                         ║
║ AÇÃO CORRETIVA:                                                         ║
║ {acao if acao else '—'}{' ' * (60 - len(acao if acao else '—'))}║
║                                                                         ║
║ LOCALIZAÇÃO: {galpao} - {room}{' ' * (48 - len(f"{galpao} - {room}"))}║
║                                                                         ║
║ ETIQUETA STELLANTIS: {etiqueta if etiqueta else '—'}{' ' * (45 - len(etiqueta if etiqueta else '—'))}║
║                                                                         ║
║ SERIAL NUMBER: {serial if serial else '—'}{' ' * (48 - len(serial if serial else '—'))}║
╚════════════════════════════════════════════════════════════════════════╝
"""
        
        if self.subs_var.get() and hasattr(self, 'inst_vars') and hasattr(self, 'rec_vars'):
            resumo += f"""
╔══════════════════════════════════════════════════════════════════╗
║                    EQUIPAMENTO RECOLHIDO                         ║
╠══════════════════════════════════════════════════════════════════╣
║ SERIAL: {serial if serial else '—'}{' ' * (60 - len(serial if serial else '—'))}║
║                                                                   ║
║ ITEM DE CONFIGURAÇÃO: {etiqueta if etiqueta else '—'}{' ' * (46 - len(etiqueta if etiqueta else '—'))}║
║                                                                   ║
║ ETIQUETA: {etiqueta if etiqueta else '—'}{' ' * (57 - len(etiqueta if etiqueta else '—'))}║
║                                                                   ║
║ MODELO: {self.rec_vars.get('Modelo:', tk.StringVar()).get()}{' ' * (59 - len(self.rec_vars.get('Modelo:', tk.StringVar()).get()))}║
║                                                                   ║
║ FLOOR: {self.rec_vars.get('Floor:', tk.StringVar()).get()}{' ' * (60 - len(self.rec_vars.get('Floor:', tk.StringVar()).get()))}║
║                                                                   ║
║ ROOM: {self.rec_vars.get('Room:', tk.StringVar()).get()}{' ' * (61 - len(self.rec_vars.get('Room:', tk.StringVar()).get()))}║
║                                                                   ║
║ IP: N/A{' ' * 62}║
║                                                                   ║
║ ESTADO: {self.rec_vars.get('Estado:', tk.StringVar()).get()}{' ' * (59 - len(self.rec_vars.get('Estado:', tk.StringVar()).get()))}║
║                                                                   ║
║ SUBESTADO: {self.rec_vars.get('Subestado:', tk.StringVar()).get()}{' ' * (56 - len(self.rec_vars.get('Subestado:', tk.StringVar()).get()))}║
║                                                                   ║
║ FUNÇÃO: N/A{' ' * 59}║
╠══════════════════════════════════════════════════════════════════╣
║                    EQUIPAMENTO INSTALADO                         ║
╠══════════════════════════════════════════════════════════════════╣
║ SERIAL: {self.inst_vars.get('Serial:', tk.StringVar()).get()}{' ' * (59 - len(self.inst_vars.get('Serial:', tk.StringVar()).get()))}║
║                                                                   ║
║ ITEM DE CONFIGURAÇÃO: {self.inst_vars.get('Item de Configuração:', tk.StringVar()).get()}{' ' * (46 - len(self.inst_vars.get('Item de Configuração:', tk.StringVar()).get()))}║
║                                                                   ║
║ ETIQUETA: {self.inst_vars.get('Item de Configuração:', tk.StringVar()).get()}{' ' * (57 - len(self.inst_vars.get('Item de Configuração:', tk.StringVar()).get()))}║
║                                                                   ║
║ MODELO: {self.inst_vars.get('Modelo:', tk.StringVar()).get()}{' ' * (59 - len(self.inst_vars.get('Modelo:', tk.StringVar()).get()))}║
║                                                                   ║
║ FLOOR: {self.inst_vars.get('Floor:', tk.StringVar()).get()}{' ' * (60 - len(self.inst_vars.get('Floor:', tk.StringVar()).get()))}║
║                                                                   ║
║ ROOM: {self.inst_vars.get('Room:', tk.StringVar()).get()}{' ' * (61 - len(self.inst_vars.get('Room:', tk.StringVar()).get()))}║
║                                                                   ║
║ IP: {self.inst_vars.get('IP:', tk.StringVar()).get()}{' ' * (63 - len(self.inst_vars.get('IP:', tk.StringVar()).get()))}║
║                                                                   ║
║ ESTADO: {self.inst_vars.get('Estado:', tk.StringVar()).get()}{' ' * (59 - len(self.inst_vars.get('Estado:', tk.StringVar()).get()))}║
║                                                                   ║
║ SUBESTADO: {self.inst_vars.get('Subestado:', tk.StringVar()).get()}{' ' * (56 - len(self.inst_vars.get('Subestado:', tk.StringVar()).get()))}║
║                                                                   ║
║ FUNÇÃO: {self.inst_vars.get('Função:', tk.StringVar()).get()}{' ' * (58 - len(self.inst_vars.get('Função:', tk.StringVar()).get()))}║
║                                                                   ║
║ APLICAÇÃO: {self.inst_vars.get('Aplicação:', tk.StringVar()).get()}{' ' * (56 - len(self.inst_vars.get('Aplicação:', tk.StringVar()).get()))}║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        self.resumo_text.insert("1.0", resumo)
        self.schedule_resumo_update()
    
    def copiar_resumo(self):
        self.resumo_text.tag_add("sel", "1.0", "end")
        self.resumo_text.event_generate("<<Copy>>")
        self.resumo_text.tag_remove("sel", "1.0", "end")
        messagebox.showinfo("Sucesso", "Resumo copiado para área de transferência!")

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroAtividadesApp(root)
    root.mainloop()