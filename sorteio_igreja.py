import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import random
import os
from datetime import datetime, timedelta

ARQUIVO_DADOS = "dados.json"

# ==================================================
# FUNÇÕES DE ARMAZENAMENTO
# ==================================================
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"membros": [], "grupos": {}, "sorteios": []}
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
        return json.load(f)

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
    dados["membros"].append(nome)
    salvar_dados(dados)
    atualizar_listas()
    messagebox.showinfo("Sucesso", f"Membro '{nome}' adicionado com sucesso!")

def adicionar_grupo():
    nome_grupo = simpledialog.askstring("Novo Grupo", "Nome do grupo:")
    if not nome_grupo:
        return
    if nome_grupo in dados["grupos"]:
        messagebox.showwarning("Aviso", "Esse grupo já existe!")
        return
    dados["grupos"][nome_grupo] = []
    salvar_dados(dados)
    atualizar_listas()
    messagebox.showinfo("Sucesso", f"Grupo '{nome_grupo}' criado com sucesso!")

def adicionar_membro_ao_grupo():
    if not dados["membros"]:
        messagebox.showwarning("Aviso", "Nenhum membro cadastrado!")
        return
    if not dados["grupos"]:
        messagebox.showwarning("Aviso", "Nenhum grupo cadastrado!")
        return

    membro = simpledialog.askstring("Adicionar ao Grupo", f"Membros disponíveis:\n{', '.join(dados['membros'])}\n\nDigite o nome do membro:")
    grupo = simpledialog.askstring("Adicionar ao Grupo", f"Grupos disponíveis:\n{', '.join(dados['grupos'].keys())}\n\nDigite o nome do grupo:")
    
    if not membro or not grupo:
        return
    if membro not in dados["membros"]:
        messagebox.showerror("Erro", "Membro não encontrado!")
        return
    if grupo not in dados["grupos"]:
        messagebox.showerror("Erro", "Grupo não encontrado!")
        return
    if membro in dados["grupos"][grupo]:
        messagebox.showinfo("Aviso", "Esse membro já está nesse grupo!")
        return

    dados["grupos"][grupo].append(membro)
    salvar_dados(dados)
    atualizar_listas()
    messagebox.showinfo("Sucesso", f"Membro '{membro}' adicionado ao grupo '{grupo}' com sucesso!")

# ==================================================
# FUNÇÃO DE SORTEIO
# ==================================================
def gerar_sorteio():
    if not dados["membros"]:
        messagebox.showwarning("Aviso", "Cadastre membros primeiro!")
        return
    
    horarios = []
    hora = datetime.strptime("00:00", "%H:%M")
    for _ in range(96):  # 96 intervalos de 15 minutos
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(minutes=15)

    # Identificar restrições
    restritos = set()
    if dados["sorteios"]:
        ultimo_sorteio = dados["sorteios"][-1]
        for h, nome in ultimo_sorteio["resultados"].items():
            if "00:00" <= h <= "06:00":
                restritos.add(nome)

    resultados = {}
    for h in horarios:
        candidatos = [m for m in dados["membros"]]
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
    exibir_sorteio(sorteio)

# ==================================================
# FUNÇÃO DE EXIBIÇÃO
# ==================================================
def exibir_sorteio(sorteio):
    janela_sorteio = tk.Toplevel(root)
    janela_sorteio.title(f"Sorteio - {sorteio['data']}")
    janela_sorteio.geometry("400x600")

    tree = ttk.Treeview(janela_sorteio, columns=("Horario", "Membro"), show="headings")
    tree.heading("Horario", text="Horário")
    tree.heading("Membro", text="Membro")
    tree.column("Horario", width=100)
    tree.column("Membro", width=250)
    tree.pack(fill="both", expand=True)

    for h, nome in sorteio["resultados"].items():
        tree.insert("", "end", values=(h, nome))

def ver_sorteios_anteriores():
    if not dados["sorteios"]:
        messagebox.showinfo("Info", "Nenhum sorteio encontrado.")
        return

    janela_hist = tk.Toplevel(root)
    janela_hist.title("Sorteios Anteriores")
    janela_hist.geometry("300x400")

    for s in dados["sorteios"]:
        tk.Button(janela_hist, text=s["data"], command=lambda s=s: exibir_sorteio(s)).pack(pady=5, fill="x")

# ==================================================
# INTERFACE
# ==================================================
def atualizar_listas():
    membros_list.delete(0, tk.END)
    for m in dados["membros"]:
        membros_list.insert(tk.END, m)
    
    grupos_list.delete(0, tk.END)
    for g, membros in dados["grupos"].items():
        grupos_list.insert(tk.END, f"{g} ({len(membros)} membros)")

# ==================================================
# INÍCIO
# ==================================================
dados = carregar_dados()

root = tk.Tk()
root.title("Sorteio de Oração da Igreja")
root.geometry("500x500")

tk.Label(root, text="Membros", font=("Arial", 12, "bold")).pack()
membros_list = tk.Listbox(root, height=5)
membros_list.pack(fill="x", padx=10, pady=5)

tk.Button(root, text="Adicionar Membro", command=adicionar_membro).pack(pady=2)

tk.Label(root, text="Grupos", font=("Arial", 12, "bold")).pack()
grupos_list = tk.Listbox(root, height=5)
grupos_list.pack(fill="x", padx=10, pady=5)

tk.Button(root, text="Criar Grupo", command=adicionar_grupo).pack(pady=2)
tk.Button(root, text="Adicionar Membro ao Grupo", command=adicionar_membro_ao_grupo).pack(pady=2)

tk.Label(root, text="Sorteio", font=("Arial", 12, "bold")).pack(pady=10)
tk.Button(root, text="Gerar Novo Sorteio", command=gerar_sorteio).pack(pady=5)
tk.Button(root, text="Ver Sorteios Anteriores", command=ver_sorteios_anteriores).pack(pady=5)

atualizar_listas()
root.mainloop()
