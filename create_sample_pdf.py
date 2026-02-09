from reportlab.pdfgen import canvas
import os

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.setTitle("Relatório Financeiro Song Technologic Solutions")
    
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "Relatório Financeiro Confidencial - Song Technologic Solutions")
    
    # Body
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Este documento contém informações sobre o desempenho financeiro.")
    
    # Relevant content for the query
    c.drawString(100, 700, "O faturamento da Empresa Song Technologic Solutions foi de 10 milhões de reais em 2023.")
    c.drawString(100, 680, "A empresa expandiu suas operações para 3 novos países.")
    
    # Irrelevant content
    c.drawString(100, 640, "Notas de rodapé: O clima organizacional permanece estável.")
    
    c.save()
    print(f"PDF criado com sucesso: {filename}")

if __name__ == "__main__":
    try:
        create_pdf("document.pdf")
    except ImportError:
        print("Erro: reportlab não está instalado.")
        print("Instale com: pip install reportlab")
