import streamlit as st
import pandas as pd
from st_keyup import st_keyup
from datetime import datetime

@st.cache_data
def load_hardware_data():
    try:
        return pd.read_csv("alm_hardware.csv", low_memory=False, encoding="latin1")
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="Registro de Atividades", layout="wide")

# CSS para centralizar títulos e abas (Visual Limpo)
st.markdown("""
    <style>
    /* Centraliza títulos e headers */
    .stTitle, .stHeader, h1, h2, h3 {
        text-align: center !important;
    }
    
    /* Centraliza a barra de abas (estilo padrão) */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
    }
    
    /* Ajusta altura das áreas de texto para compactar */
    .stTextArea textarea {
        height: 100px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📒 Registro de Atividades")

# ✅ ÚNICA CORREÇÃO - Usar session_state para persistir os dados
if 'atividades' not in st.session_state:
    st.session_state.atividades = []
atividades = st.session_state.atividades

# Abas horizontais
aba1, aba5, aba2, aba3, aba4 = st.tabs(["📌 Cadastro", "📄 Resumo Atual", "📋 Registros", "🔄 Substituições", "🌐 Host"])

# Aba Cadastro
with aba1:
    st.header("REGISTRO DE ATIVIDADES")

    # Sistema para limpar o formulário ao registrar
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    fk = st.session_state.form_key

    # Reset last_etiqueta quando o formulário é limpo (nova fk)
    if 'last_fk' not in st.session_state:
        st.session_state.last_fk = fk
    if st.session_state.last_fk != fk:
        st.session_state.last_fk = fk
        st.session_state.last_etiqueta = ""
        st.session_state.has_autofilled_subs = False

    # Mostra mensagem de sucesso se acabou de registrar
    if st.session_state.get('show_success', False):
        st.success("Atividade registrada com sucesso!")
        st.session_state.show_success = False

    # Layout dinâmico: Centralizado se normal, 3 colunas se substituição ativa
    is_subs = st.session_state.get(f"subs_{fk}", False)
    
    if is_subs:
        col1, col2, col3 = st.columns([1, 1, 1])
    else:
        # Cria colunas para centralizar o formulário no meio da tela
        c_v1, c_v2, c_v3 = st.columns([1, 2, 1])
        col1 = c_v2

    with col1:
        st.subheader("📝 Dados da Atividade")
        descricao_falha = st.text_area("Descrição da Falha", key=f"desc_{fk}", height=100)
        acao_corretiva = st.text_area("Ação Corretiva", key=f"acao_{fk}", height=100)
        df_host = load_hardware_data()
        
        etiqueta = st.text_input("Etiiqueta Stellantis (CI)", key=f"etiq_{fk}")
        
        if 'last_etiqueta' not in st.session_state:
            st.session_state.last_etiqueta = ""

        # Busca os dados no Host
        found_match = False
        fetched_serial = fetched_galpao = fetched_room = fetched_modelo = ""
        if etiqueta and not df_host.empty:
            match = df_host[df_host['ci'].astype(str).str.strip().str.upper() == etiqueta.strip().upper()]
            if not match.empty:
                found_match = True
                row = match.iloc[0]
                fetched_serial = str(row['serial_number']) if pd.notna(row['serial_number']) else ""
                fetched_galpao = str(row['u_floor']) if pd.notna(row['u_floor']) else ""
                fetched_room = str(row['u_room']) if pd.notna(row['u_room']) else ""
                fetched_modelo = str(row['display_name']) if pd.notna(row['display_name']) else ""

        # Trigger de preenchimento quando a etiqueta muda
        if etiqueta != st.session_state.last_etiqueta:
            st.session_state.last_etiqueta = etiqueta
            st.session_state.has_autofilled_subs = False # Reset flag para permitir novo preenchimento
            if found_match:
                st.session_state[f"serial_{fk}"] = fetched_serial
                st.session_state[f"galpao_{fk}"] = fetched_galpao
                st.session_state[f"room_{fk}"] = fetched_room
                # Injeta também nos campos de substituição
                st.session_state[f"rec_modelo_{fk}"] = fetched_modelo
                st.session_state[f"inst_florr_{fk}"] = fetched_galpao
                st.session_state[f"inst_room_{fk}"] = fetched_room

        if etiqueta and not df_host.empty:
            if found_match:
                st.success("✅ Host OK!")
            else:
                st.warning("⚠️ Não encontrado.")

        serial = st.text_input("Serial", key=f"serial_{fk}")
        galpao = st.text_input("Galpão", key=f"galpao_{fk}")
        room_setor = st.text_input("Room/Setor", key=f"room_{fk}")
        solicitante = st.text_input("Solicitante", key=f"solic_{fk}")

        # Checkbox para substituição
        equipamento_substituido = st.checkbox("Equipamento Substituído", key=f"subs_{fk}")

    # Inicializa variáveis para evitar erro no dicionário de atividades
    eq_serial = eq_ip = eq_item_config = eq_modelo = eq_florr = eq_room = eq_aplicacao = ""
    eq_estado = eq_substato = eq_funcao = ""
    rec_modelo = rec_florr = rec_room = rec_estado = rec_substato = ""

    if is_subs:
        # Se temos um match e ainda não preenchemos os campos de substituição deste chamado
        if found_match and not st.session_state.get('has_autofilled_subs', False):
            st.session_state[f"rec_modelo_{fk}"] = fetched_modelo
            st.session_state[f"inst_florr_{fk}"] = fetched_galpao
            st.session_state[f"inst_room_{fk}"] = fetched_room
            st.session_state.has_autofilled_subs = True

        with col2:
            st.subheader("➡️ Instalado")
            eq_serial = st.text_input("Serial", key=f"inst_serial_{fk}")
            eq_ip = st.text_input("IP", key=f"inst_ip_{fk}")
            eq_item_config = st.text_input("Item de Configuração", key=f"inst_item_config_{fk}")
            eq_modelo = st.text_input("Modelo", key=f"inst_modelo_{fk}")
            eq_florr = st.text_input("Floor", key=f"inst_florr_{fk}")
            eq_room = st.text_input("Room", key=f"inst_room_{fk}")
            eq_aplicacao = st.text_input("Aplicação", key=f"inst_aplicacao_{fk}")
            eq_estado = st.text_input("Estado", value="Em uso", key=f"inst_estado_{fk}")
            eq_substato = st.text_input("Subestado", value="Disponível", key=f"inst_substato_{fk}")
            eq_funcao = st.text_input("Função", value="Compartilhado", key=f"inst_funcao_{fk}")

        with col3:
            st.subheader("⬅️ Recolhido")
            rec_modelo = st.text_input("Modelo", key=f"rec_modelo_{fk}")
            rec_florr = st.text_input("Floor", value="Galpão 01", key=f"rec_florr_{fk}")
            rec_room = st.text_input("Room", value="Sala 12 (Laboratório Atos)", key=f"rec_room_{fk}")
            rec_estado = st.text_input("Estado", value="Em estoque", key=f"rec_estado_{fk}")
            rec_substato = st.text_input("Subestado", value="Recuperação pendente", key=f"rec_substato_{fk}")

    # Botão de Registrar centralizado no final
    st.markdown("---")
    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        registrar = st.button("🚀 Registrar Atividade", use_container_width=True)

    if registrar:
        data_atual = datetime.now().strftime("%d/%m/%Y")
        atividades.append({
            "Descrição da falha": descricao_falha,
            "Ação corretiva": acao_corretiva,
            "Etiqueta": etiqueta,
            "Serial": serial,
            "Galpão": galpao,
            "Room/Setor": room_setor,
            "Solicitante": solicitante,
            "Equipamento substituído": equipamento_substituido,
            "Data": data_atual,
            "Eq Serial": eq_serial,
            "Eq IP": eq_ip,
            "Eq Item Config": eq_item_config,
            "Eq Estado": eq_estado,
            "Eq Modelo": eq_modelo,
            "Eq Substato": eq_substato,
            "Eq Florr": eq_florr,
            "Eq Função": eq_funcao,
            "Eq Room": eq_room,
            "Eq Aplicação": eq_aplicacao,
            "Rec Modelo": rec_modelo,
            "Rec Florr": rec_florr,
            "Rec Room": rec_room,
            "Rec Estado": rec_estado,
            "Rec Substato": rec_substato
        })
        # Incrementa o key para limpar o formulário
        st.session_state.form_key += 1
        st.session_state.show_success = True
        st.rerun()

# Aba Registros
with aba2:
    st.header("📋 Registros")
    if atividades:
        registros_formatados = []
        for a in atividades:
            registros_formatados.append({
                "DESCRIÇÃO DA FALHA": a.get("Descrição da falha", ""),
                "AÇÃO CORRETIVA": a.get("Ação corretiva", ""),
                "SETOR": a.get("Room/Setor", ""),
                "GALPÃO / COLUNA": a.get("Galpão", ""),
                "CELULAR": "(31)9 95426967",
                "ETIQUETA STELLANTIS": a.get("Etiqueta", ""),
                "SERIAL NUMBER": a.get("Serial", ""),
                "DATA": a.get("Data", datetime.now().strftime("%d/%m/%Y")),
                "CHAMADO": a.get("Chamado", "")
            })
            
        df = pd.DataFrame(registros_formatados)
        st.write("💡 Você pode editar a tabela abaixo diretamente (ex: adicionar o CHAMADO) clicando nas células:")
        edited_df = st.data_editor(df, use_container_width=True, key="editor_registros")

        edited_df = edited_df.fillna("")

        # Salva as edições de volta na lista atividades para não perder ao recarregar a tela
        for i, row in edited_df.iterrows():
            if i < len(atividades):
                atividades[i]["Descrição da falha"] = row["DESCRIÇÃO DA FALHA"]
                atividades[i]["Ação corretiva"] = row["AÇÃO CORRETIVA"]
                atividades[i]["Room/Setor"] = row["SETOR"]
                atividades[i]["Galpão"] = row["GALPÃO / COLUNA"]
                atividades[i]["Etiqueta"] = row["ETIQUETA STELLANTIS"]
                atividades[i]["Serial"] = row["SERIAL NUMBER"]
                atividades[i]["Data"] = row["DATA"]
                atividades[i]["Chamado"] = row["CHAMADO"]

        # Atualiza a lista de dicionários com os valores editados para usar nos blocos de cópia
        edited_registros = edited_df.to_dict('records')

        with st.expander("📋 Copiar Todos"):
            textos = []
            for r in edited_registros:
                texto_item = (
                    f"DESCRIÇÃO DA FALHA: {r['DESCRIÇÃO DA FALHA']}\n"
                    f"AÇÃO CORRETIVA: {r['AÇÃO CORRETIVA']}\n"
                    f"SETOR: {r['SETOR']}\n"
                    f"GALPÃO / COLUNA: {r['GALPÃO / COLUNA']}\n"
                    f"CELULAR: {r['CELULAR']}\n"
                    f"ETIQUETA STELLANTIS: {r['ETIQUETA STELLANTIS']}\n"
                    f"SERIAL NUMBER: {r['SERIAL NUMBER']}\n"
                    f"DATA: {r['DATA']}\n"
                    f"CHAMADO: {r['CHAMADO']}"
                )
                textos.append(texto_item)
            
            st.info("Passe o mouse sobre o bloco abaixo e clique no ícone de copiar.")
            st.code("\n\n----------------------------------------\n\n".join(textos), language="text")

        if st.button("🗑️ Limpar registros"):
            atividades.clear()
            st.warning("Registros apagados!")
            st.rerun()

        st.subheader("Gerenciar individualmente")
        for i, a in enumerate(atividades):
            col1, col2 = st.columns([4, 1])
            col1.write(f"{a.get('Descrição da falha', '')} - {a.get('Solicitante', '')}")
            if col2.button("🗑️ Apagar", key=f"del{i}"):
                atividades.pop(i)
                st.warning(f"Registro {i+1} apagado!")
                st.rerun()
            with st.expander(f"📋 Mostrar texto para copiar (Registro {i+1})"):
                r = edited_registros[i]
                texto_item = (
                    f"DESCRIÇÃO DA FALHA: {r['DESCRIÇÃO DA FALHA']}\n"
                    f"AÇÃO CORRETIVA: {r['AÇÃO CORRETIVA']}\n"
                    f"SETOR: {r['SETOR']}\n"
                    f"GALPÃO / COLUNA: {r['GALPÃO / COLUNA']}\n"
                    f"CELULAR: {r['CELULAR']}\n"
                    f"ETIQUETA STELLANTIS: {r['ETIQUETA STELLANTIS']}\n"
                    f"SERIAL NUMBER: {r['SERIAL NUMBER']}\n"
                    f"DATA: {r['DATA']}\n"
                    f"CHAMADO: {r['CHAMADO']}"
                )
                st.code(texto_item, language="text")
    else:
        st.info("Nenhum registro ainda.")

# Aba Substituições
with aba3:
    st.header("🔄 Substituições")
    subs = [a for a in atividades if a["Equipamento substituído"] == True]
    if subs:
        df = pd.DataFrame(subs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhuma substituição registrada.")

# Aba Host
with aba4:
    st.header("🌐 Host")
    df_host = load_hardware_data()
    
    if not df_host.empty:
        st.write(f"Total de equipamentos registrados: **{len(df_host)}**")
        
        # Seleciona e renomeia as colunas desejadas
        colunas_exibicao = {
            'ci': 'Item de Configuração',
            'u_room': 'ROOM',
            'u_floor': 'FLOOR',
            'serial_number': 'Numero de Serie',
            'display_name': 'Modelo'
        }
        
        # Mantém apenas as colunas que realmente existem no arquivo
        colunas_disponiveis = {k: v for k, v in colunas_exibicao.items() if k in df_host.columns}
        df_exibicao = df_host[list(colunas_disponiveis.keys())].rename(columns=colunas_disponiveis)
        
        # Utiliza st_keyup para busca em tempo real sem precisar apertar Enter
        busca = st_keyup("🔍 Buscar por Serial, Etiqueta (Asset Tag) ou CI", key="busca_host")
        
        if busca:
            # Filtra por texto (case-insensitive) nas 3 colunas principais do dataframe original
            mask = (
                df_host['serial_number'].astype(str).str.contains(busca, case=False, na=False) |
                df_host['asset_tag'].astype(str).str.contains(busca, case=False, na=False) |
                df_host['ci'].astype(str).str.contains(busca, case=False, na=False)
            )
            # Aplica o filtro no dataframe de exibição
            df_filtered = df_exibicao[mask]
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        else:
            st.info("Mostrando os primeiros 100 registros. Use a barra de busca acima para encontrar equipamentos específicos.")
            st.dataframe(df_exibicao.head(100), use_container_width=True, hide_index=True)
    else:
        st.error("Não foi possível carregar o arquivo `alm_hardware.csv`. Verifique se ele está na mesma pasta do projeto.")

# Aba Resumo Atual
with aba5:
    st.header("📄 Resumo Atual")
    st.info("Resumo dos dados da atividade atual. Se o formulário estiver limpo, mostra o último registro salvo.")
    
    form_preenchido = any([descricao_falha, acao_corretiva, etiqueta, serial, galpao, room_setor, solicitante])
    
    if form_preenchido:
        resumo_descricao_falha = descricao_falha
        resumo_room_setor = room_setor
        resumo_galpao = galpao
        resumo_etiqueta = etiqueta
        resumo_serial = serial
        resumo_solicitante = solicitante
        resumo_acao_corretiva = acao_corretiva
        resumo_equipamento_substituido = equipamento_substituido
        resumo_rec_modelo = rec_modelo
        resumo_rec_florr = rec_florr
        resumo_rec_room = rec_room
        resumo_rec_estado = rec_estado
        resumo_rec_substato = rec_substato
        resumo_eq_serial = eq_serial
        resumo_eq_item_config = eq_item_config
        resumo_eq_modelo = eq_modelo
        resumo_eq_florr = eq_florr
        resumo_eq_room = eq_room
        resumo_eq_ip = eq_ip
        resumo_eq_estado = eq_estado
        resumo_eq_substato = eq_substato
        resumo_eq_funcao = eq_funcao
        resumo_eq_aplicacao = eq_aplicacao
    elif atividades:
        ultima = atividades[-1]
        resumo_descricao_falha = ultima.get("Descrição da falha", "")
        resumo_room_setor = ultima.get("Room/Setor", "")
        resumo_galpao = ultima.get("Galpão", "")
        resumo_etiqueta = ultima.get("Etiqueta", "")
        resumo_serial = ultima.get("Serial", "")
        resumo_solicitante = ultima.get("Solicitante", "")
        resumo_acao_corretiva = ultima.get("Ação corretiva", "")
        resumo_equipamento_substituido = ultima.get("Equipamento substituído", False)
        resumo_rec_modelo = ultima.get("Rec Modelo", "")
        resumo_rec_florr = ultima.get("Rec Florr", "")
        resumo_rec_room = ultima.get("Rec Room", "")
        resumo_rec_estado = ultima.get("Rec Estado", "")
        resumo_rec_substato = ultima.get("Rec Substato", "")
        resumo_eq_serial = ultima.get("Eq Serial", "")
        resumo_eq_item_config = ultima.get("Eq Item Config", "")
        resumo_eq_modelo = ultima.get("Eq Modelo", "")
        resumo_eq_florr = ultima.get("Eq Florr", "")
        resumo_eq_room = ultima.get("Eq Room", "")
        resumo_eq_ip = ultima.get("Eq IP", "")
        resumo_eq_estado = ultima.get("Eq Estado", "")
        resumo_eq_substato = ultima.get("Eq Substato", "")
        resumo_eq_funcao = ultima.get("Eq Função", "")
        resumo_eq_aplicacao = ultima.get("Eq Aplicação", "")
    else:
        resumo_descricao_falha = ""
        resumo_room_setor = ""
        resumo_galpao = ""
        resumo_etiqueta = ""
        resumo_serial = ""
        resumo_solicitante = ""
        resumo_acao_corretiva = ""
        resumo_equipamento_substituido = False
        resumo_rec_modelo = ""
        resumo_rec_florr = ""
        resumo_rec_room = ""
        resumo_rec_estado = ""
        resumo_rec_substato = ""
        resumo_eq_serial = ""
        resumo_eq_item_config = ""
        resumo_eq_modelo = ""
        resumo_eq_florr = ""
        resumo_eq_room = ""
        resumo_eq_ip = ""
        resumo_eq_estado = ""
        resumo_eq_substato = ""
        resumo_eq_funcao = ""
        resumo_eq_aplicacao = ""

    texto_resumo = f"""ABERTURA
DESCRIÇÃO: {resumo_descricao_falha}
SETOR: {resumo_room_setor}
GALPÃO: {resumo_galpao}
CELULAR: (31)9 95426967
ETIQUETA STELLANTIS: {resumo_etiqueta}
SERIAL NUMBER: {resumo_serial}
SOLICITANTE: {resumo_solicitante}

ENCERRAMENTO
FALHA: {resumo_descricao_falha}
AÇÃO CORRETIVA: {resumo_acao_corretiva}
LOCALIZAÇÃO: {resumo_galpao} - {resumo_room_setor}
ETIQUETA STELLANTIS: {resumo_etiqueta}
SERIAL NUMBER: {resumo_serial}
"""

    if resumo_equipamento_substituido:
        texto_resumo += f"""
Equipamento Recolhido
SERIAL: {resumo_serial}
ITEM DE CONFIGURAÇÃO: {resumo_etiqueta}
ETIQUETA: {resumo_etiqueta}
MODELO: {resumo_rec_modelo}
FLOOR: {resumo_rec_florr}
ROOM: {resumo_rec_room}
IP: 
ESTADO: {resumo_rec_estado}
SUBESTADO: {resumo_rec_substato}
FUNÇÃO: 

Equipamento Instalado
SERIAL: {resumo_eq_serial}
ITEM DE CONFIGURAÇÃO: {resumo_eq_item_config}
ETIQUETA: {resumo_eq_item_config}
MODELO: {resumo_eq_modelo}
FLOOR: {resumo_eq_florr}
ROOM: {resumo_eq_room}
IP: {resumo_eq_ip}
ESTADO: {resumo_eq_estado}
SUBESTADO: {resumo_eq_substato}
FUNÇÃO: {resumo_eq_funcao}
APLICAÇÃO: {resumo_eq_aplicacao}
"""
    
    st.code(texto_resumo, language="text")
