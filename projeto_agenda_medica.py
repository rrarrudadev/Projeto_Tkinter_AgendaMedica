import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

DB_FILE = "agenda_medica.db"

# Banco de dados
def get_connection():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def init_db():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS medico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        especialidade TEXT,
        telefone TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS paciente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT,
        telefone TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS consulta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medico_id INTEGER NOT NULL,
        paciente_id INTEGER NOT NULL,
        datahora TEXT NOT NULL,
        motivo TEXT,
        FOREIGN KEY (medico_id) REFERENCES medico(id) ON DELETE CASCADE,
        FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
    );
    """)

    con.commit()
    con.close()

# CRUD

# Médicos
def inserir_medico(nome, especialidade, telefone):
    if not nome.strip():
        raise ValueError("Nome do médico é obrigatório")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO medico (nome, especialidade, telefone) VALUES (?,?,?)",
                (nome.strip(), especialidade.strip(), telefone.strip()))
    conn.commit()
    conn.close()

def listar_medicos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM medico ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows

def deletar_medico(medico_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM medico WHERE id=?", (medico_id,))
    conn.commit()
    conn.close()

# Pacientes
def inserir_paciente(nome, cpf, telefone):
    if not nome.strip():
        raise ValueError("Nome do paciente é obrigatório")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO paciente (nome, cpf, telefone) VALUES (?,?,?)",
                (nome.strip(), cpf.strip(), telefone.strip()))
    conn.commit()
    conn.close()

def listar_pacientes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM paciente ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows

def deletar_paciente(paciente_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM paciente WHERE id=?", (paciente_id,))
    conn.commit()
    conn.close()

# Consultas
def inserir_consulta(medico_id, paciente_id, datahora, motivo):
    try:
        # validar formato YYYY-MM-DD HH:MM
        datetime.strptime(datahora, "%Y-%m-%d %H:%M")
    except Exception as e:
        raise ValueError("Data/hora inválida. Use formato: YYYY-MM-DD HH:MM")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO consulta (medico_id, paciente_id, datahora, motivo) VALUES (?,?,?,?)",
                (medico_id, paciente_id, datahora, motivo.strip()))
    conn.commit()
    conn.close()

def listar_consultas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.datahora, c.motivo, m.id AS medico_id, m.nome AS medico_nome,
               p.id AS paciente_id, p.nome AS paciente_nome
        FROM consulta c
        JOIN medico m ON c.medico_id = m.id
        JOIN paciente p ON c.paciente_id = p.id
        ORDER BY c.datahora
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def deletar_consulta(consulta_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM consulta WHERE id=?", (consulta_id,))
    conn.commit()
    conn.close()

# Interface
class AgendaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agenda Médica")
        self.geometry("900x600")

        # Menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(label="Médicos", command=lambda: self.show_frame("medicos"))
        nav_menu.add_command(label="Pacientes", command=lambda: self.show_frame("pacientes"))
        nav_menu.add_command(label="Consultas", command=lambda: self.show_frame("consultas"))
        menubar.add_cascade(label="Navegar", menu=nav_menu)

        ajuda_menu = tk.Menu(menubar, tearoff=0)
        ajuda_menu.add_command(label="Créditos / Sobre", command=self.show_about)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)

        # Container para frames
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F, name in [(MedicosFrame, "medicos"), (PacientesFrame, "pacientes"), (ConsultasFrame, "consultas")]:
            frame = F(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("medicos")

    def show_frame(self, name):
        frame = self.frames.get(name)
        if frame:
            frame.refresh()
            frame.tkraise()

    def show_about(self):
        texto = (
            "Agenda Médica\n\n"
            "Integrantes:\n"
            " - Lucas Leonardo Martins Farias\n"
            " - Rafael Rocha Arruda\n\n"
            "Desafio 3 – Agenda Médica\n\n"
            "Descrição:\n"
            "Aplicação de cadastro de médicos, pacientes e agendamento de consultas.\n"
        )
        messagebox.showinfo("Créditos / Sobre", texto)

# Frame Médicos
class MedicosFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Label(self, text="Gestão de Médicos", font=(None, 16))
        header.pack(pady=10)

        form = ttk.Frame(self)
        form.pack(fill="x", padx=20)

        ttk.Label(form, text="Nome:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_nome = ttk.Entry(form)
        self.entry_nome.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Especialidade:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_esp = ttk.Entry(form)
        self.entry_esp.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Telefone:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_tel = ttk.Entry(form)
        self.entry_tel.grid(row=2, column=1, sticky="ew", pady=2)

        form.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=8)
        ttk.Button(btn_frame, text="Adicionar Médico", command=self.adicionar_medico).pack(side="left")
        ttk.Button(btn_frame, text="Remover Selecionado", command=self.remover_selecionado).pack(side="left", padx=8)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("id","nome","especialidade","telefone"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("especialidade", text="Especialidade")
        self.tree.heading("telefone", text="Telefone")
        self.tree.column("id", width=50, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def adicionar_medico(self):
        nome = self.entry_nome.get()
        esp = self.entry_esp.get()
        tel = self.entry_tel.get()
        try:
            inserir_medico(nome, esp, tel)
            messagebox.showinfo("Sucesso", "Médico adicionado com sucesso")
            self.entry_nome.delete(0, tk.END)
            self.entry_esp.delete(0, tk.END)
            self.entry_tel.delete(0, tk.END)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def remover_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um médico na lista")
            return
        item = self.tree.item(sel[0])
        medico_id = item['values'][0]
        if messagebox.askyesno("Confirmação", "Deseja remover o médico selecionado? Isso também removerá consultas vinculadas."):
            deletar_medico(medico_id)
            self.refresh()

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for m in listar_medicos():
            self.tree.insert("", tk.END, values=(m['id'], m['nome'], m['especialidade'], m['telefone']))

# Frame Pacientes
class PacientesFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Label(self, text="Gestão de Pacientes", font=(None, 16))
        header.pack(pady=10)

        form = ttk.Frame(self)
        form.pack(fill="x", padx=20)

        ttk.Label(form, text="Nome:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_nome = ttk.Entry(form)
        self.entry_nome.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="CPF:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_dn = ttk.Entry(form)
        self.entry_dn.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Telefone:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_tel = ttk.Entry(form)
        self.entry_tel.grid(row=2, column=1, sticky="ew", pady=2)

        form.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=8)
        ttk.Button(btn_frame, text="Adicionar Paciente", command=self.adicionar_paciente).pack(side="left")
        ttk.Button(btn_frame, text="Remover Selecionado", command=self.remover_selecionado).pack(side="left", padx=8)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("id","nome","cpf","telefone"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("cpf", text="CPF")
        self.tree.heading("telefone", text="Telefone")
        self.tree.column("id", width=50, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def adicionar_paciente(self):
        nome = self.entry_nome.get()
        dn = self.entry_dn.get()
        tel = self.entry_tel.get()
        try:
            # Validação da data
            if dn.strip():
                datetime.strptime(dn.strip(), "%Y-%m-%d")
            inserir_paciente(nome, dn, tel)
            messagebox.showinfo("Sucesso", "Paciente adicionado com sucesso")
            self.entry_nome.delete(0, tk.END)
            self.entry_dn.delete(0, tk.END)
            self.entry_tel.delete(0, tk.END)
            self.refresh()
        except ValueError as ve:
            messagebox.showerror("Erro", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def remover_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um paciente na lista")
            return
        item = self.tree.item(sel[0])
        paciente_id = item['values'][0]
        if messagebox.askyesno("Confirmação", "Deseja remover o paciente selecionado? Isso também removerá consultas vinculadas."):
            deletar_paciente(paciente_id)
            self.refresh()

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for p in listar_pacientes():
            self.tree.insert("", tk.END, values=(p['id'], p['nome'], p['cpf'], p['telefone']))

# Frame Consultas
class ConsultasFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Label(self, text="Agendamento de Consultas", font=(None, 16))
        header.pack(pady=10)

        form = ttk.Frame(self)
        form.pack(fill="x", padx=20)

        ttk.Label(form, text="Médico:").grid(row=0, column=0, sticky="w", pady=2)
        self.cb_medico = ttk.Combobox(form, state="readonly")
        self.cb_medico.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Paciente:").grid(row=1, column=0, sticky="w", pady=2)
        self.cb_paciente = ttk.Combobox(form, state="readonly")
        self.cb_paciente.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Data e Hora (YYYY-MM-DD HH:MM):").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_dt = ttk.Entry(form)
        self.entry_dt.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Motivo:").grid(row=3, column=0, sticky="w", pady=2)
        self.entry_motivo = ttk.Entry(form)
        self.entry_motivo.grid(row=3, column=1, sticky="ew", pady=2)

        form.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=8)
        ttk.Button(btn_frame, text="Agendar Consulta", command=self.agendar_consulta).pack(side="left")
        ttk.Button(btn_frame, text="Remover Selecionado", command=self.remover_selecionado).pack(side="left", padx=8)

        # Treeview
        columns = ("id","datahora","medico","paciente","motivo")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("datahora", text="Data/Hora")
        self.tree.heading("medico", text="Médico")
        self.tree.heading("paciente", text="Paciente")
        self.tree.heading("motivo", text="Motivo")
        self.tree.column("id", width=50, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def agendar_consulta(self):
        med = self.cb_medico.get()
        pac = self.cb_paciente.get()
        dt = self.entry_dt.get()
        motivo = self.entry_motivo.get()
        if not med or not pac:
            messagebox.showwarning("Aviso", "Escolha um médico e um paciente")
            return
        try:
            medico_id = int(med.split(':',1)[0])
            paciente_id = int(pac.split(':',1)[0])
            inserir_consulta(medico_id, paciente_id, dt, motivo)
            messagebox.showinfo("Sucesso", "Consulta agendada com sucesso")
            self.entry_dt.delete(0, tk.END)
            self.entry_motivo.delete(0, tk.END)
            self.refresh()
        except ValueError as ve:
            messagebox.showerror("Erro", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def remover_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma consulta na lista")
            return
        item = self.tree.item(sel[0])
        consulta_id = item['values'][0]
        if messagebox.askyesno("Confirmação", "Deseja remover a consulta selecionada?"):
            deletar_consulta(consulta_id)
            self.refresh()

    def refresh(self):
        # Atualiza comboboxes
        med_list = [f"{m['id']}: {m['nome']} ({m['especialidade'] or ''})" for m in listar_medicos()]
        pac_list = [f"{p['id']}: {p['nome']}" for p in listar_pacientes()]
        self.cb_medico['values'] = med_list
        self.cb_paciente['values'] = pac_list

        # Atualiza treeview
        for r in self.tree.get_children():
            self.tree.delete(r)
        for c in listar_consultas():
            # Formatar data
            try:
                dt = datetime.strptime(c['datahora'], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
            except Exception:
                dt = c['datahora']
            self.tree.insert("", tk.END, values=(c['id'], dt, c['medico_nome'], c['paciente_nome'], c['motivo']))

# Execução
if __name__ == '__main__':
    init_db()
    app = AgendaApp()
    app.mainloop()
