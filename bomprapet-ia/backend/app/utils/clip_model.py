# app/utils/clip_model.py
import torch
import clip
from PIL import Image

# Carregar modelo CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Conjunto base de frases
base_descricoes = [
    "um cachorro pequeno",
    "um cachorro grande",
    "um gato pequeno",
    "um gato grande",
    "um cachorro marrom",
    "um gato preto",
    "um animal branco",
    "um cachorro com coleira",
    "um gato dormindo",
    "um cachorro brincalhão",
    "um gato de olhos claros"
]

def gerar_descricao_clip(caminho_imagem):
    """Gera uma descrição baseada nas legendas mais próximas da imagem."""
    image = preprocess(Image.open(caminho_imagem)).unsqueeze(0).to(device)
    text = clip.tokenize(base_descricoes).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)
        similarity = (image_features @ text_features.T).squeeze(0)
        indice_max = similarity.argmax().item()
        descricao = base_descricoes[indice_max]

    return descricao