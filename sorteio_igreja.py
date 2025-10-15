import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import random
import os
from datetime import datetime, timedelta
import pyperclip
from fpdf import FPDF

ARQUIVO_DADOS = "dados.json"

DARK_BG = "#2b2d30"
ENTRY_BG = "#3c3f41"
LIST_BG = "#313335"
TEXT_FG = "#ffffff"
SELECT_BG = "#4a4d50"

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def get_horarios():
    horarios = []
    hora = datetime.strptime("00:00", "%H:%M")
    for _ in range(96):
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(minutes=15)
    return horarios

# ==================================================
# FUNÇÕES DE ARMAZENAMENTO
# ==================================================
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"membros": [], "grupos": {}, "sorteios": [], "restricoes_horarios": {}}
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
        dados = json.load(f)
        if "restricoes_horarios" not in dados:
            dados["restricoes_horarios"] = {}
        return dados

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# ==================================================
# FUNÇÕES DE CADASTRO
# ==================================================
def adicionar_membro():
    nome = simpledialog.askstring("Novo Membro", "Nome do membro:")
    if not nome:
        return

    # Janela para marcar horários restritos
    window = tk.Toplevel(root)
    window.title(f"Marque os horários restritos para {nome}")
    window.geometry("300x500")
    window.configure(bg=DARK_BG)

    canvas_frame = tk.Frame(window, bg=DARK_BG)
    canvas_frame.pack(fill='both', expand=True)

    canvas = tk.Canvas(canvas_frame, bg=DARK_BG)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=DARK_BG)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    horarios = get_horarios()
    check_vars = {}

    for h in horarios:
        var = tk.IntVar(value=0)
        chk = tk.Checkbutton(scrollable_frame, text=h, variable=var, onvalue=1, offvalue=0,
                             bg=DARK_BG, fg=TEXT_FG, selectcolor=SELECT_BG,
                             activebackground=DARK_BG, activeforeground=TEXT_FG)
        chk.pack(anchor='w', padx=10, pady=2)
        check_vars[h] = var

    def salvar_membro():
        restricoes = [h for h, var in check_vars.items() if var.get() == 1]
        dados["membros"].append(nome)
        dados["restricoes_horarios"][nome] = restricoes
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", f"Membro '{nome}' adicionado com sucesso!")
        window.destroy()
        if current_tab == 'membros':
            show_frame('membros')

    tk.Button(window, text="Salvar", command=salvar_membro, bg=ENTRY_BG, fg=TEXT_FG, width=20).pack(pady=10)

def adicionar_grupo():
    nome_grupo = simpledialog.askstring("Novo Grupo", "Nome do grupo:")
    if not nome_grupo:
        return
    if nome_grupo in dados["grupos"]:
        messagebox.showwarning("Aviso", "Esse grupo já existe!")
        return
    dados["grupos"][nome_grupo] = []
    salvar_dados(dados)
    messagebox.showinfo("Sucesso", f"Grupo '{nome_grupo}' criado com sucesso!")
    if current_tab == 'membros':
        show_frame('membros')

def adicionar_membro_ao_grupo_specific(membro):
    if not membro:
        return
    if not dados["grupos"]:
        messagebox.showwarning("Aviso", "Nenhum grupo cadastrado!")
        return

    # Janela para selecionar grupo com tamanho ajustado
    window = tk.Toplevel(root)
    window.title(f"Adicionar {membro} a um grupo")
    window.geometry("400x150")  # Aumentado para 400x150
    window.configure(bg=DARK_BG)

    tk.Label(window, text="Selecione o grupo:", bg=DARK_BG, fg=TEXT_FG).pack(pady=20)

    grupos_var = tk.StringVar(value="")
    combobox = ttk.Combobox(window, textvariable=grupos_var, values=list(dados["grupos"].keys()), state="readonly")
    combobox.pack(pady=20)

    def salvar_selecao():
        grupo = grupos_var.get()
        if not grupo:
            messagebox.showwarning("Aviso", "Selecione um grupo!")
            return
        if membro in dados["grupos"][grupo]:
            messagebox.showinfo("Aviso", "Esse membro já está nesse grupo!")
            window.destroy()
            return
        dados["grupos"][grupo].append(membro)
        salvar_dados(dados)
        if current_tab == 'membros':
            show_frame('membros')
        messagebox.showinfo("Sucesso", f"Membro '{membro}' adicionado ao grupo '{grupo}' com sucesso!")
        window.destroy()

    tk.Button(window, text="Adicionar", command=salvar_selecao, bg=ENTRY_BG, fg=TEXT_FG, width=20).pack(pady=20)

def gerenciar_restricoes(membro):
    if not membro:
        return
    window = tk.Toplevel(root)
    window.title(f"Restrições de Horário para {membro}")
    window.geometry("300x500")
    window.configure(bg=DARK_BG)

    canvas_frame = tk.Frame(window, bg=DARK_BG)
    canvas_frame.pack(fill='both', expand=True)

    canvas = tk.Canvas(canvas_frame, bg=DARK_BG)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=DARK_BG)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    horarios = get_horarios()
    restricoes = set(dados["restricoes_horarios"].get(membro, []))

    check_vars = {}
    for h in horarios:
        var = tk.IntVar(value=1 if h in restricoes else 0)
        chk = tk.Checkbutton(scrollable_frame, text=h, variable=var, onvalue=1, offvalue=0,
                             bg=DARK_BG, fg=TEXT_FG, selectcolor=SELECT_BG,
                             activebackground=DARK_BG, activeforeground=TEXT_FG)
        chk.pack(anchor='w', padx=10, pady=2)
        check_vars[h] = var

    def salvar_restricoes():
        novas_restricoes = [h for h, var in check_vars.items() if var.get() == 1]
        dados["restricoes_horarios"][membro] = novas_restricoes
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", "Restrições de horário atualizadas com sucesso!")
        window.destroy()

    tk.Button(window, text="Salvar", command=salvar_restricoes, bg=ENTRY_BG, fg=TEXT_FG, width=20).pack(pady=10)

# ==================================================
# FUNÇÃO DE SORTEIO
# ==================================================
def gerar_sorteio():
    if not dados["membros"]:
        messagebox.showwarning("Aviso", "Cadastre membros primeiro!")
        return
    
    horarios = get_horarios()

    # Identificar restrições de madrugada do último sorteio
    restritos = set()
    if dados["sorteios"]:
        ultimo_sorteio = dados["sorteios"][-1]
        for h, nome in ultimo_sorteio["resultados"].items():
            if "00:00" <= h <= "06:00" and nome != "—":
                restritos.add(nome)

    resultados = {}
    for h in horarios:
        # Aplicar restrições individuais
        candidatos = [m for m in dados["membros"] if h not in dados["restricoes_horarios"].get(m, [])]
        # Aplicar restrição de repetição para madrugada
        if "00:00" <= h <= "06:00":
            candidatos = [m for m in candidatos if m not in restritos]
        if not candidatos:
            resultados[h] = "—"
        else:
            escolhido = random.choice(candidatos)
            resultados[h] = escolhido

    sorteio = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "resultados": resultados
    }

    dados["sorteios"].append(sorteio)
    salvar_dados(dados)
    global just_generated
    just_generated = True
    show_frame('historico')

# ==================================================
# FUNÇÃO PARA COPIAR TEXTO
# ==================================================
def copiar_texto_sorteio(sorteio):
    texto = f"Sorteio - {sorteio['data']}\n\n"
    texto += "Geral:\n"
    for h, nome in sorteio["resultados"].items():
        texto += f"{h}: {nome}\n"
    texto += "\n"
    for grupo, membros_grupo in dados["grupos"].items():
        texto += f"{grupo}:\n"
        for h, nome in sorteio["resultados"].items():
            if nome in membros_grupo:
                texto += f"{h}: {nome}\n"
        texto += "\n"
    pyperclip.copy(texto)
    messagebox.showinfo("Sucesso", "Texto do sorteio copiado para a área de transferência!")

# ==================================================
# FUNÇÃO PARA GERAR PDF
# ==================================================
def gerar_pdf_sorteio(sorteio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Sorteio - {sorteio['data']}", ln=1, align='C')
    
    pdf.set_font("Arial", 'B', size=10)
    pdf.cell(200, 10, txt="Geral:", ln=1)
    pdf.set_font("Arial", size=10)
    for h, nome in sorteio["resultados"].items():
        # Substituir "—" por "-" para evitar erro de codificação
        nome_seguro = nome.replace("—", "-")
        pdf.cell(200, 10, txt=f"{h}: {nome_seguro}", ln=1)
    
    for grupo, membros_grupo in dados["grupos"].items():
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(200, 10, txt=f"{grupo}:", ln=1)
        pdf.set_font("Arial", size=10)
        for h, nome in sorteio["resultados"].items():
            if nome in membros_grupo:
                nome_seguro = nome.replace("—", "-")
                pdf.cell(200, 10, txt=f"{h}: {nome_seguro}", ln=1)
    
    file_path = f"sorteio_{sorteio['data'].replace('/', '-').replace(':', '-')}.pdf"
    pdf.output(file_path)
    messagebox.showinfo("Sucesso", f"PDF gerado com sucesso: {file_path}")

# ==================================================
# FUNÇÃO DE EXIBIÇÃO
# ==================================================
def show_sorteio_in_frame(sorteio, frame):
    for w in frame.winfo_children():
        w.destroy()

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True)

    # Aba Geral
    geral_frame = tk.Frame(notebook, bg=DARK_BG)
    notebook.add(geral_frame, text="Geral")

    tree_geral = ttk.Treeview(geral_frame, columns=("Horario", "Membro"), show="headings")
    tree_geral.heading("Horario", text="Horário")
    tree_geral.heading("Membro", text="Membro")
    tree_geral.column("Horario", width=100)
    tree_geral.column("Membro", width=250)
    tree_geral.pack(fill="both", expand=True)

    for h, nome in sorteio["resultados"].items():
        tree_geral.insert("", "end", values=(h, nome))

    # Abas por Grupo
    for grupo, membros_grupo in dados["grupos"].items():
        grupo_frame = tk.Frame(notebook, bg=DARK_BG)
        notebook.add(grupo_frame, text=grupo)

        tree_grupo = ttk.Treeview(grupo_frame, columns=("Horario", "Membro"), show="headings")
        tree_grupo.heading("Horario", text="Horário")
        tree_grupo.heading("Membro", text="Membro")
        tree_grupo.column("Horario", width=100)
        tree_grupo.column("Membro", width=250)
        tree_grupo.pack(fill="both", expand=True)

        for h, nome in sorteio["resultados"].items():
            if nome in membros_grupo:
                tree_grupo.insert("", "end", values=(h, nome))

    # Botões para copiar e baixar
    buttons_frame = tk.Frame(frame, bg=DARK_BG)
    buttons_frame.pack(fill='x', pady=10)

    tk.Button(buttons_frame, text="Copiar Texto", command=lambda: copiar_texto_sorteio(sorteio), bg=ENTRY_BG, fg=TEXT_FG, width=15).pack(side='left', padx=10)
    tk.Button(buttons_frame, text="Baixar PDF", command=lambda: gerar_pdf_sorteio(sorteio), bg=ENTRY_BG, fg=TEXT_FG, width=15).pack(side='left', padx=10)

# ==================================================
# INTERFACE
# ==================================================
def show_frame(tab):
    global current_tab
    current_tab = tab
    for w in main_frame.winfo_children():
        w.destroy()

    if tab == 'home':
        home_content()
    elif tab == 'membros':
        membros_content()
    elif tab == 'historico':
        historico_content()

def home_content():
    label = tk.Label(main_frame, text="Sorteio de Oração da Igreja", font=("Arial", 16, "bold"), bg=DARK_BG, fg=TEXT_FG)
    label.pack(pady=50)

    membros_frame = tk.Frame(main_frame, bg=DARK_BG)
    membros_frame.pack(fill='x', padx=20, pady=10)

    tk.Label(membros_frame, text="Membros", font=("Arial", 12, "bold"), bg=DARK_BG, fg=TEXT_FG).pack()

    search = tk.Entry(membros_frame, bg=ENTRY_BG, fg='grey', insertbackground=TEXT_FG)
    search.pack(fill='x', pady=5)
    search.insert(0, "Buscar membros...")

    def on_focus_in(event):
        if search.get() == "Buscar membros...":
            search.delete(0, tk.END)
            search.config(fg=TEXT_FG)

    def on_focus_out(event):
        if search.get() == "":
            search.insert(0, "Buscar membros...")
            search.config(fg='grey')

    search.bind("<FocusIn>", on_focus_in)
    search.bind("<FocusOut>", on_focus_out)

    membros_list = tk.Listbox(membros_frame, bg=LIST_BG, fg=TEXT_FG, selectbackground=SELECT_BG, width=50, height=20)
    membros_list.pack(fill='both', expand=True)

    def update_membros_list(query=''):
        membros_list.delete(0, tk.END)
        actual_query = query if query != "Buscar membros..." else ""
        for m in dados["membros"]:
            if actual_query.lower() in m.lower() or not actual_query:
                membros_list.insert(tk.END, m)

    update_membros_list(search.get())

    search.bind('<KeyRelease>', lambda e: update_membros_list(search.get()))

    # Menu de contexto para membros
    membros_menu = tk.Menu(root, tearoff=0, bg=ENTRY_BG, fg=TEXT_FG)
    membros_menu.add_command(label="Adicionar a Grupo", command=lambda: adicionar_membro_ao_grupo_specific(get_selected_member()))
    membros_menu.add_command(label="Gerenciar Restrições de Horário", command=lambda: gerenciar_restricoes(get_selected_member()))

    def get_selected_member():
        sel = membros_list.curselection()
        if sel:
            return membros_list.get(sel[0])
        return None

    def show_membros_menu(e):
        try:
            idx = membros_list.nearest(e.y)
            if idx >= 0:
                membros_list.selection_clear(0, tk.END)
                membros_list.selection_set(idx)
                membros_list.activate(idx)
                membros_menu.post(e.x_root, e.y_root)
        except:
            pass

    membros_list.bind("<Button-3>", show_membros_menu)
    membros_list.bind("<Double-1>", show_membros_menu)

    tk.Button(main_frame, text="Gerar Novo Sorteio", command=gerar_sorteio, bg=ENTRY_BG, fg=TEXT_FG, width=20).pack(pady=10)

def membros_content():
    left = tk.Frame(main_frame, bg=DARK_BG)
    left.pack(side='left', fill='y', padx=20, pady=10)

    tk.Label(left, text="Membros", font=("Arial", 12, "bold"), bg=DARK_BG, fg=TEXT_FG).pack()

    membros_list = tk.Listbox(left, bg=LIST_BG, fg=TEXT_FG, selectbackground=SELECT_BG, width=30, height=20)
    membros_list.pack(fill='y', expand=True)

    def update_membros_list():
        membros_list.delete(0, tk.END)
        for m in dados["membros"]:
            membros_list.insert(tk.END, m)

    update_membros_list()

    tk.Button(left, text="Adicionar Membro", command=adicionar_membro, bg=ENTRY_BG, fg=TEXT_FG, width=20).pack(pady=5)

    right = tk.Frame(main_frame, bg=DARK_BG)
    right.pack(side='left', fill='both', expand=True, padx=20, pady=10)

    tk.Label(right, text="Grupos", font=("Arial", 12, "bold"), bg=DARK_BG, fg=TEXT_FG).pack()

    grupos_list = tk.Listbox(right, bg=LIST_BG, fg=TEXT_FG, selectbackground=SELECT_BG, width=40, height=20)
    grupos_list.pack(fill='both', expand=True)

    def update_grupos_list():
        grupos_list.delete(0, tk.END)
        for g, membros in dados["grupos"].items():
            grupos_list.insert(tk.END, f"{g} ({len(membros)} membros)")

    update_grupos_list()

    tk.Button(right, text="Criar Grupo", command=adicionar_grupo, bg=ENTRY_BG, fg=TEXT_FG, width=20).pack(pady=5)

def historico_content():
    if not dados["sorteios"]:
        label = tk.Label(main_frame, text="Nenhum sorteio encontrado.", font=("Arial", 12), bg=DARK_BG, fg=TEXT_FG)
        label.pack(pady=50)
        return

    left = tk.Frame(main_frame, bg=DARK_BG)
    left.pack(side='left', fill='y', padx=20, pady=10)

    tk.Label(left, text="Sorteios Anteriores", font=("Arial", 12, "bold"), bg=DARK_BG, fg=TEXT_FG).pack()

    hist_list = tk.Listbox(left, bg=LIST_BG, fg=TEXT_FG, selectbackground=SELECT_BG, width=30, height=20)
    hist_list.pack(fill='y', expand=True)

    for s in dados["sorteios"]:
        hist_list.insert(tk.END, s["data"])

    right = tk.Frame(main_frame, bg=DARK_BG)
    right.pack(side='left', fill='both', expand=True, padx=20, pady=10)

    tk.Label(right, text="Detalhes do Sorteio", font=("Arial", 12, "bold"), bg=DARK_BG, fg=TEXT_FG).pack()

    tree_frame = tk.Frame(right, bg=DARK_BG)
    tree_frame.pack(fill='both', expand=True)

    def on_select(e=None):
        sel = hist_list.curselection()
        if sel:
            idx = sel[0]
            sorteio = dados["sorteios"][idx]
            show_sorteio_in_frame(sorteio, tree_frame)

    hist_list.bind('<<ListboxSelect>>', on_select)

    global just_generated
    if just_generated:
        hist_list.select_set(len(dados["sorteios"]) - 1)
        on_select()
        just_generated = False

# ==================================================
# INÍCIO
# ==================================================
dados = carregar_dados()

root = tk.Tk()
root.title("Sorteio de Oração da Igreja")
root.geometry("800x600")
root.configure(bg=DARK_BG)

style = ttk.Style()
style.configure("Treeview", background=LIST_BG, foreground=TEXT_FG, fieldbackground=LIST_BG, rowheight=25)
style.configure("Treeview.Heading", background=ENTRY_BG, foreground=TEXT_FG)
style.map("Treeview", background=[('selected', SELECT_BG)], foreground=[('selected', TEXT_FG)])

top_frame = tk.Frame(root, bg=DARK_BG)
top_frame.pack(fill='x', pady=5)

home_btn = tk.Button(top_frame, text="Home", bg=DARK_BG, fg=TEXT_FG, borderwidth=0, command=lambda: show_frame('home'))
home_btn.pack(side='left', padx=10)

membros_btn = tk.Button(top_frame, text="Membros", bg=DARK_BG, fg=TEXT_FG, borderwidth=0, command=lambda: show_frame('membros'))
membros_btn.pack(side='left', padx=10)

historico_btn = tk.Button(top_frame, text="Historico", bg=DARK_BG, fg=TEXT_FG, borderwidth=0, command=lambda: show_frame('historico'))
historico_btn.pack(side='left', padx=10)

logo = tk.Label(top_frame, text="Igreja", bg=DARK_BG, fg=TEXT_FG, font=("Arial", 14, "bold"))
logo.pack(side='right', padx=10)

main_frame = tk.Frame(root, bg=DARK_BG)
main_frame.pack(fill='both', expand=True)

current_tab = 'home'
just_generated = False

show_frame('home')
root.mainloop()