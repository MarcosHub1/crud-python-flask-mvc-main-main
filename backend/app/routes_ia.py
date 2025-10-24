# app/routes_ia.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from app.utils.clip_model import gerar_descricao_clip

ia_bp = Blueprint('ia_bp', __name__)

@ia_bp.route("/api/descrever", methods=["POST"])
def descrever_imagem():
    """
    Rota de teste do CLIP: recebe uma imagem e retorna a descrição automática.
    """
    if "imagem" not in request.files:
        return jsonify({"erro": "Envie uma imagem no campo 'imagem'"}), 400

    imagem = request.files["imagem"]

    # Salvar imagem temporariamente
    nome_arquivo = f"{uuid.uuid4().hex}_{imagem.filename}"
    caminho = os.path.join(current_app.root_path, "static/uploads", nome_arquivo)
    imagem.save(caminho)

    try:
        descricao = gerar_descricao_clip(caminho)
        return jsonify({
            "descricao_gerada": descricao,
            "imagem_salva": nome_arquivo
        })
    except Exception as e:
        print("Erro ao processar imagem:", e)
        return jsonify({"erro": str(e)}), 500
