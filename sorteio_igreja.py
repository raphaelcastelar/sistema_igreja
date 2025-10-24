import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import random
import os
from datetime import datetime, timedelta
import pyperclip
from fpdf import FPDF

ARQUIVO_DADOS = "dados.json"

# Paleta de cores
PRIMARY_BG = "#1E2A44"
ACCENT_BG = "#2E4057"
HIGHLIGHT = "#FFD700"
TEXT_COLOR = "#FFFFFF"
SELECT_COLOR = "#4A6FA5"

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def get_horarios_restricao():
    horarios = []
    hora = datetime.strptime("00:00", "%H:%M")
    for _ in range(24):
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(hours=1)
    return horarios

def get_horarios_sorteio():
    horarios = []
    hora = datetime.strptime("00:00", "%H:%M")
    for _ in range(96):
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(minutes=15)
    return horarios

# ==================================================
# ARMAZENAMENTO
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
# CADASTRO DE MEMBRO
# ==================================================
def adicionar_membro():
    nome = simpledialog.askstring("Novo Membro", "Nome do membro:", parent=root)
    if not nome:
        return

    window = tk.Toplevel(root)
    window.title(f"Restrições de {nome}")
    window.geometry("380x500")
    window.configure(bg=PRIMARY_BG)
    window.resizable(False, False)

    main_container = tk.Frame(window, bg=PRIMARY_BG)
    main_container.pack(fill='both', expand=True, padx=15, pady=15)

    canvas_frame = tk.Frame(main_container, bg=PRIMARY_BG)
    canvas_frame.pack(fill='both', expand=True)

    canvas = tk.Canvas(canvas_frame, bg=PRIMARY_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview, style="Custom.Vertical.TScrollbar")
    scrollable_frame = tk.Frame(canvas, bg=PRIMARY_BG)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    horarios = get_horarios_restricao()
    check_vars = {}

    for h in horarios:
        var = tk.IntVar(value=0)
        chk = tk.Checkbutton(scrollable_frame, text=h, variable=var, onvalue=1, offvalue=0,
                             bg=PRIMARY_BG, fg=TEXT_COLOR, selectcolor=SELECT_COLOR,
                             activebackground=ACCENT_BG, activeforeground=TEXT_COLOR,
                             font=("Arial", 11, "bold"))
        chk.pack(anchor='w', padx=10, pady=8)
        check_vars[h] = var

    button_frame = tk.Frame(main_container, bg=PRIMARY_BG)
    button_frame.pack(fill='x', pady=(15, 0))

    def salvar_membro_e_adicionar_grupo():
        restricoes = [h for h, var in check_vars.items() if var.get() == 1]
        dados["membros"].append(nome)
        dados["restricoes_horarios"][nome] = restricoes
        salvar_dados(dados)
        window.destroy()
        adicionar_a_grupo(nome)

    tk.Button(button_frame, text="Salvar e Adicionar a Grupo", command=salvar_membro_e_adicionar_grupo,
              bg=HIGHLIGHT, fg=PRIMARY_BG, font=("Arial", 12, "bold"), width=30, relief="flat").pack(pady=5)

def adicionar_a_grupo(membro):
    if not dados["grupos"]:
        messagebox.showinfo("Informação", "Nenhum grupo cadastrado. Crie um grupo primeiro!", parent=root)
        if current_tab == 'membros':
            show_frame('membros')
        return

    grupo_window = tk.Toplevel(root)
    grupo_window.title(f"Adicionar {membro} a um grupo")
    grupo_window.geometry("450x200")
    grupo_window.configure(bg=PRIMARY_BG)

    tk.Label(grupo_window, text="Selecione o grupo:", bg=PRIMARY_BG, fg=TEXT_COLOR,
             font=("Arial", 12, "bold")).pack(pady=20)

    grupos_var = tk.StringVar(value="")
    combobox = ttk.Combobox(grupo_window, textvariable=grupos_var, values=list(dados["grupos"].keys()),
                            state="readonly", style="Custom.TCombobox")
    combobox.pack(pady=20)

    def salvar_selecao():
        grupo = grupos_var.get()
        if not grupo:
            messagebox.showwarning("Aviso", "Selecione um grupo!", parent=root)
            return
        if membro in dados["grupos"][grupo]:
            messagebox.showinfo("Aviso", "Membro já está nesse grupo!", parent=root)
            grupo_window.destroy()
            return
        dados["grupos"][grupo].append(membro)
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", f"'{membro}' adicionado a '{grupo}'!", parent=root)
        grupo_window.destroy()
        if current_tab == 'membros':
            show_frame('membros')

    tk.Button(grupo_window, text="Adicionar", command=salvar_selecao, bg=HIGHLIGHT, fg=PRIMARY_BG,
              font=("Arial", 12, "bold"), width=15, relief="flat").pack(pady=20)

def adicionar_grupo():
    nome_grupo = simpledialog.askstring("Novo Grupo", "Nome do grupo:", parent=root)
    if not nome_grupo:
        return
    if nome_grupo in dados["grupos"]:
        messagebox.showwarning("Aviso", "Grupo já existe!", parent=root)
        return
    dados["grupos"][nome_grupo] = []
    salvar_dados(dados)
    messagebox.showinfo("Sucesso", f"'{nome_grupo}' criado!", parent=root)
    if current_tab == 'membros':
        show_frame('membros')

def adicionar_membro_ao_grupo_specific(membro):
    if not membro or not dados["grupos"]:
        messagebox.showwarning("Aviso", "Nenhum grupo cadastrado!" if not dados["grupos"] else "Selecione um membro!", parent=root)
        return

    window = tk.Toplevel(root)
    window.title(f"Adicionar {membro} a um grupo")
    window.geometry("450x200")
    window.configure(bg=PRIMARY_BG)

    tk.Label(window, text="Selecione o grupo:", bg=PRIMARY_BG, fg=TEXT_COLOR,
             font=("Arial", 12, "bold")).pack(pady=20)

    grupos_var = tk.StringVar(value="")
    combobox = ttk.Combobox(window, textvariable=grupos_var, values=list(dados["grupos"].keys()),
                            state="readonly", style="Custom.TCombobox")
    combobox.pack(pady=20)

    def salvar_selecao():
        grupo = grupos_var.get()
        if not grupo:
            messagebox.showwarning("Aviso", "Selecione um grupo!", parent=root)
            return
        if membro in dados["grupos"][grupo]:
            messagebox.showinfo("Aviso", "Membro já está nesse grupo!", parent=root)
            window.destroy()
            return
        dados["grupos"][grupo].append(membro)
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", f"'{membro}' adicionado a '{grupo}'!", parent=root)
        window.destroy()
        if current_tab == 'membros':
            show_frame('membros')

    tk.Button(window, text="Adicionar", command=salvar_selecao, bg=HIGHLIGHT, fg=PRIMARY_BG,
              font=("Arial", 12, "bold"), width=15, relief="flat").pack(pady=20)

def gerenciar_restricoes(membro):
    if not membro:
        return
    window = tk.Toplevel(root)
    window.title(f"Restrições de {membro}")
    window.geometry("380x500")
    window.configure(bg=PRIMARY_BG)
    window.resizable(False, False)

    main_container = tk.Frame(window, bg=PRIMARY_BG)
    main_container.pack(fill='both', expand=True, padx=15, pady=15)

    canvas_frame = tk.Frame(main_container, bg=PRIMARY_BG)
    canvas_frame.pack(fill='both', expand=True)

    canvas = tk.Canvas(canvas_frame, bg=PRIMARY_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview, style="Custom.Vertical.TScrollbar")
    scrollable_frame = tk.Frame(canvas, bg=PRIMARY_BG)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    horarios = get_horarios_restricao()
    restricoes = set(dados["restricoes_horarios"].get(membro, []))

    check_vars = {}
    for h in horarios:
        var = tk.IntVar(value=1 if h in restricoes else 0)
        chk = tk.Checkbutton(scrollable_frame, text=h, variable=var, onvalue=1, offvalue=0,
                             bg=PRIMARY_BG, fg=TEXT_COLOR, selectcolor=SELECT_COLOR,
                             activebackground=ACCENT_BG, activeforeground=TEXT_COLOR,
                             font=("Arial", 11, "bold"))
        chk.pack(anchor='w', padx=10, pady=8)
        check_vars[h] = var

    button_frame = tk.Frame(main_container, bg=PRIMARY_BG)
    button_frame.pack(fill='x', pady=(15, 0))

    def salvar_restricoes():
        novas_restricoes = [h for h, var in check_vars.items() if var.get() == 1]
        dados["restricoes_horarios"][membro] = novas_restricoes
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", "Restrições atualizadas!", parent=root)
        window.destroy()

    tk.Button(button_frame, text="Salvar", command=salvar_restricoes,
              bg=HIGHLIGHT, fg=PRIMARY_BG, font=("Arial", 12, "bold"), width=20, relief="flat").pack(pady=5)

# ==================================================
# EXCLUIR MEMBRO
# ==================================================
def excluir_membro(nome):
    if not nome or not messagebox.askyesno("Confirmar", f"Excluir '{nome}'?", parent=root):
        return
    if nome in dados["membros"]:
        dados["membros"].remove(nome)
    if nome in dados["restricoes_horarios"]:
        del dados["restricoes_horarios"][nome]
    for grupo in dados["grupos"]:
        if nome in dados["grupos"][grupo]:
            dados["grupos"][grupo].remove(nome)
    salvar_dados(dados)
    messagebox.showinfo("Sucesso", f"'{nome}' excluído!", parent=root)
    show_frame(current_tab)

# ==================================================
# REMOVER MEMBRO DO GRUPO
# ==================================================
def remover_membro_do_grupo(grupo, membro):
    if not messagebox.askyesno("Remover", f"Remover '{membro}' do grupo '{grupo}'?", parent=root):
        return
    if membro in dados["grupos"][grupo]:
        dados["grupos"][grupo].remove(membro)
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", f"'{membro}' removido de '{grupo}'!", parent=root)

# ==================================================
# SORTEIO
# ==================================================
def gerar_sorteio():
    if not dados["membros"]:
        messagebox.showwarning("Aviso", "Cadastre membros primeiro!", parent=root)
        return
    
    horarios = get_horarios_sorteio()
    restritos = set()
    if dados["sorteios"]:
        ultimo_sorteio = dados["sorteios"][-1]
        for h, nome in ultimo_sorteio["resultados"].items():
            if "00:00" <= h <= "06:00" and nome != "—":
                restritos.add(nome)

    resultados = {}
    membros_sorteados = set()

    for h in horarios:
        hora_cheia = h.split(":")[0] + ":00"
        candidatos = [m for m in dados["membros"] if m not in membros_sorteados and hora_cheia not in dados["restricoes_horarios"].get(m, [])]
        if "00:00" <= h <= "06:00":
            candidatos = [m for m in candidatos if m not in restritos]
        if not candidatos:
            resultados[h] = "—"
        else:
            escolhido = random.choice(candidatos)
            resultados[h] = escolhido
            membros_sorteados.add(escolhido)

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
# EXPORTAÇÃO
# ==================================================
def copiar_texto_sorteio(sorteio):
    texto = f"Sorteio - {sorteio['data']}\n\nGeral:\n"
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
    messagebox.showinfo("Sucesso", "Texto copiado!", parent=root)

def gerar_pdf_sorteio(sorteio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Sorteio - {sorteio['data']}", ln=1, align='C')
    pdf.set_font("Arial", 'B', size=10)
    pdf.cell(200, 10, txt="Geral:", ln=1)
    pdf.set_font("Arial", size=10)
    for h, nome in sorteio["resultados"].items():
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
    messagebox.showinfo("Sucesso", f"PDF gerado: {file_path}", parent=root)

# ==================================================
# EXIBIÇÃO DO SORTEIO
# ==================================================
def show_sorteio_in_frame(sorteio, frame):
    for w in frame.winfo_children():
        w.destroy()

    notebook = ttk.Notebook(frame, style="Custom.TNotebook")
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    geral_frame = tk.Frame(notebook, bg=PRIMARY_BG)
    notebook.add(geral_frame, text="Geral")

    tree_geral = ttk.Treeview(geral_frame, columns=("Horario", "Membro"), show="headings", style="Custom.Treeview")
    tree_geral.heading("Horario", text="Horário")
    tree_geral.heading("Membro", text="Membro")
    tree_geral.column("Horario", width=120)
    tree_geral.column("Membro", width=280)
    tree_geral.pack(fill="both", expand=True, padx=10, pady=10)

    for h, nome in sorteio["resultados"].items():
        tree_geral.insert("", "end", values=(h, nome))

    for grupo, membros_grupo in dados["grupos"].items():
        grupo_frame = tk.Frame(notebook, bg=PRIMARY_BG)
        notebook.add(grupo_frame, text=f"{grupo}")

        tree_grupo = ttk.Treeview(grupo_frame, columns=("Horario", "Membro"), show="headings", style="Custom.Treeview")
        tree_grupo.heading("Horario", text="Horário")
        tree_grupo.heading("Membro", text="Membro")
        tree_grupo.column("Horario", width=120)
        tree_grupo.column("Membro", width=280)
        tree_grupo.pack(fill="both", expand=True, padx=10, pady=10)

        for h, nome in sorteio["resultados"].items():
            if nome in membros_grupo:
                tree_grupo.insert("", "end", values=(h, nome))

    buttons_frame = tk.Frame(frame, bg=PRIMARY_BG)
    buttons_frame.pack(fill='x', pady=15)

    tk.Button(buttons_frame, text="Copiar", command=lambda: copiar_texto_sorteio(sorteio), bg=HIGHLIGHT,
              fg=PRIMARY_BG, font=("Arial", 10, "bold"), width=12, relief="flat").pack(side='left', padx=5)
    tk.Button(buttons_frame, text="Baixar PDF", command=lambda: gerar_pdf_sorteio(sorteio), bg=HIGHLIGHT,
              fg=PRIMARY_BG, font=("Arial", 10, "bold"), width=12, relief="flat").pack(side='left', padx=5)

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
    label = tk.Label(main_frame, text="Sorteio de Oração", font=("Arial", 24, "bold"), bg=PRIMARY_BG,
                     fg=HIGHLIGHT, pady=20)
    label.pack()

    membros_frame = tk.Frame(main_frame, bg=PRIMARY_BG)
    membros_frame.pack(fill='x', padx=20, pady=10)

    tk.Label(membros_frame, text="Membros", font=("Arial", 16, "bold"), bg=PRIMARY_BG, fg=TEXT_COLOR).pack()

    search = tk.Entry(membros_frame, bg=ACCENT_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                      font=("Arial", 10), relief="flat")
    search.pack(fill='x', pady=5, ipady=5)
    search.insert(0, "Buscar membros...")
    search.bind("<FocusIn>", lambda e: search.delete(0, tk.END) if search.get() == "Buscar membros..." else None)
    search.bind("<FocusOut>", lambda e: search.insert(0, "Buscar membros...") if not search.get() else None)

    membros_list = tk.Listbox(membros_frame, bg=ACCENT_BG, fg=TEXT_COLOR, selectbackground=SELECT_COLOR,
                              width=50, height=20, font=("Arial", 10), relief="flat")
    membros_list.pack(fill='both', expand=True, padx=5, pady=5)

    def update_membros_list(query=''):
        membros_list.delete(0, tk.END)
        actual_query = query if query != "Buscar membros..." else ""
        for m in dados["membros"]:
            if actual_query.lower() in m.lower() or not actual_query:
                membros_list.insert(tk.END, m)

    update_membros_list(search.get())
    search.bind('<KeyRelease>', lambda e: update_membros_list(search.get()))

    membros_menu = tk.Menu(root, tearoff=0, bg=ACCENT_BG, fg=TEXT_COLOR, font=("Arial", 10))
    membros_menu.add_command(label="Adicionar a Grupo", command=lambda: adicionar_membro_ao_grupo_specific(get_selected_member()))
    membros_menu.add_command(label="Gerenciar Restrições", command=lambda: gerenciar_restricoes(get_selected_member()))
    membros_menu.add_separator()
    membros_menu.add_command(label="Excluir", command=lambda: excluir_membro(get_selected_member()))

    def get_selected_member():
        sel = membros_list.curselection()
        return membros_list.get(sel[0]) if sel else None

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

    tk.Button(main_frame, text="Gerar Sorteio", command=gerar_sorteio, bg=HIGHLIGHT, fg=PRIMARY_BG,
              font=("Arial", 12, "bold"), width=15, relief="flat").pack(pady=20)

# ==================================================
# ABA MEMBROS - SELEÇÃO INDEPENDENTE COM GRUPO SALVO
# ==================================================
def membros_content():
    global selected_group
    left = tk.Frame(main_frame, bg=PRIMARY_BG)
    left.pack(side='left', fill='y', padx=20, pady=10)

    tk.Label(left, text="Membros", font=("Arial", 16, "bold"), bg=PRIMARY_BG, fg=TEXT_COLOR).pack()

    membros_list = tk.Listbox(left, bg=ACCENT_BG, fg=TEXT_COLOR, selectbackground=SELECT_COLOR,
                              width=30, height=20, font=("Arial", 10), relief="flat", selectmode='single')
    membros_list.pack(fill='y', expand=True)

    def update_membros_list():
        membros_list.delete(0, tk.END)
        for m in dados["membros"]:
            membros_list.insert(tk.END, m)

    update_membros_list()

    tk.Button(left, text="Adicionar", command=adicionar_membro, bg=HIGHLIGHT, fg=PRIMARY_BG,
              font=("Arial", 12, "bold"), width=15, relief="flat").pack(pady=5)

    # === DIREITA ===
    right = tk.Frame(main_frame, bg=PRIMARY_BG)
    right.pack(side='left', fill='both', expand=True, padx=20, pady=10)

    tk.Label(right, text="Grupos", font=("Arial", 16, "bold"), bg=PRIMARY_BG, fg=TEXT_COLOR).pack(anchor='w')

    grupos_list = tk.Listbox(right, bg=ACCENT_BG, fg=TEXT_COLOR, selectbackground=SELECT_COLOR,
                             width=40, height=10, font=("Arial", 10), relief="flat", selectmode='single')
    grupos_list.pack(fill='x', pady=(0, 10))

    membros_grupo_frame = tk.Frame(right, bg=PRIMARY_BG)
    membros_grupo_frame.pack(fill='both', expand=True)

    tk.Label(membros_grupo_frame, text="Membros do Grupo:", font=("Arial", 14, "bold"), bg=PRIMARY_BG, fg=HIGHLIGHT).pack(anchor='w')

    membros_grupo_list = tk.Listbox(membros_grupo_frame, bg=ACCENT_BG, fg=TEXT_COLOR, selectbackground=SELECT_COLOR,
                                    width=40, height=15, font=("Arial", 10), relief="flat", selectmode='single')
    membros_grupo_list.pack(fill='both', expand=True, pady=(0, 10))

    # === VARIÁVEL GLOBAL PARA GRUPO SELECIONADO ===
    selected_group = None

    # === FUNÇÕES DE ATUALIZAÇÃO ===
    def update_grupos_list():
        grupos_list.delete(0, tk.END)
        for g, membros in dados["grupos"].items():
            grupos_list.insert(tk.END, f"{g} ({len(membros)} membros)")

    def update_membros_grupo_list():
        membros_grupo_list.delete(0, tk.END)
        if selected_group and selected_group in dados["grupos"]:
            for m in dados["grupos"][selected_group]:
                membros_grupo_list.insert(tk.END, m)

    def on_grupo_select(e=None):
        global selected_group
        sel = grupos_list.curselection()
        if sel:
            idx = sel[0]
            grupos_list.selection_set(idx)  # Mantém grupo selecionado
            selected_group = list(dados["grupos"].keys())[idx]
            update_membros_grupo_list()
            membros_grupo_list.selection_clear(0, tk.END)  # Limpa seleção de membro ao mudar grupo

    grupos_list.bind('<<ListboxSelect>>', on_grupo_select)
    update_grupos_list()

    # === SELEÇÃO DE MEMBRO SEM DESSELECIONAR GRUPO ===
    def on_membro_click(e):
        global selected_group
        if selected_group:
            idx = membros_grupo_list.nearest(e.y)
            if idx >= 0 and idx < membros_grupo_list.size():
                membros_grupo_list.selection_clear(0, tk.END)
                membros_grupo_list.selection_set(idx)
                membros_grupo_list.activate(idx)

    membros_grupo_list.bind('<Button-1>', on_membro_click)

    # === CRIAR GRUPO ===
    tk.Button(right, text="Criar Grupo", command=lambda: [adicionar_grupo(), update_grupos_list()],
              bg=HIGHLIGHT, fg=PRIMARY_BG, font=("Arial", 12, "bold"), width=15, relief="flat").pack(pady=5, anchor='w')

    # === REMOVER DO GRUPO (USANDO selected_group) ===
    def remover_do_grupo():
        global selected_group
        sel_membro = membros_grupo_list.curselection()
        if not selected_group:
            messagebox.showwarning("Aviso", "Selecione um grupo!", parent=root)
            return
        if not sel_membro:
            messagebox.showwarning("Aviso", "Selecione um membro do grupo!", parent=root)
            return

        membro = membros_grupo_list.get(sel_membro[0])
        remover_membro_do_grupo(selected_group, membro)
        update_membros_grupo_list()
        update_grupos_list()

    tk.Button(right, text="Remover do Grupo", command=remover_do_grupo,
              bg="#C0392B", fg=TEXT_COLOR, font=("Arial", 10, "bold"), width=18, relief="flat").pack(pady=5, anchor='w')

def historico_content():
    if not dados["sorteios"]:
        label = tk.Label(main_frame, text="Nenhum sorteio encontrado.", font=("Arial", 14), bg=PRIMARY_BG, fg=TEXT_COLOR)
        label.pack(pady=50)
        return

    left = tk.Frame(main_frame, bg=PRIMARY_BG)
    left.pack(side='left', fill='y', padx=20, pady=10)

    tk.Label(left, text="Sorteios", font=("Arial", 16, "bold"), bg=PRIMARY_BG, fg=TEXT_COLOR).pack()

    hist_list = tk.Listbox(left, bg=ACCENT_BG, fg=TEXT_COLOR, selectbackground=SELECT_COLOR,
                           width=30, height=20, font=("Arial", 10), relief="flat")
    hist_list.pack(fill='y', expand=True)

    for s in dados["sorteios"]:
        hist_list.insert(tk.END, s["data"])

    right = tk.Frame(main_frame, bg=PRIMARY_BG)
    right.pack(side='left', fill='both', expand=True, padx=20, pady=10)

    tk.Label(right, text="Detalhes", font=("Arial", 16, "bold"), bg=PRIMARY_BG, fg=TEXT_COLOR).pack()

    tree_frame = tk.Frame(right, bg=PRIMARY_BG)
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
root.title("Sorteio de Oração")
root.geometry("1000x700")
root.configure(bg=PRIMARY_BG)

style = ttk.Style()
style.theme_use('clam')
style.configure("Custom.TNotebook", background=PRIMARY_BG, foreground=TEXT_COLOR, borderwidth=0)
style.configure("Custom.Treeview", background=ACCENT_BG, foreground=TEXT_COLOR, fieldbackground=ACCENT_BG)
style.map("Custom.Treeview", background=[('selected', SELECT_COLOR)], foreground=[('selected', TEXT_COLOR)])
style.configure("Custom.TCombobox", fieldbackground=ACCENT_BG, background=ACCENT_BG, foreground=TEXT_COLOR)
style.configure("Custom.Vertical.TScrollbar", background=ACCENT_BG, troughcolor=PRIMARY_BG, arrowcolor=TEXT_COLOR)

top_frame = tk.Frame(root, bg=PRIMARY_BG, height=60)
top_frame.pack(fill='x')

tk.Button(top_frame, text="Home", bg=ACCENT_BG, fg=TEXT_COLOR, font=("Arial", 12), borderwidth=0,
          command=lambda: show_frame('home')).pack(side='left', padx=10, pady=10)
tk.Button(top_frame, text="Membros", bg=ACCENT_BG, fg=TEXT_COLOR, font=("Arial", 12), borderwidth=0,
          command=lambda: show_frame('membros')).pack(side='left', padx=10, pady=10)
tk.Button(top_frame, text="Histórico", bg=ACCENT_BG, fg=TEXT_COLOR, font=("Arial", 12), borderwidth=0,
          command=lambda: show_frame('historico')).pack(side='left', padx=10, pady=10)
tk.Label(top_frame, text="Igreja", bg=PRIMARY_BG, fg=HIGHLIGHT, font=("Arial", 16, "bold")).pack(side='right', padx=20, pady=10)

main_frame = tk.Frame(root, bg=PRIMARY_BG)
main_frame.pack(fill='both', expand=True)

current_tab = 'home'
just_generated = False

show_frame('home')
root.mainloop()