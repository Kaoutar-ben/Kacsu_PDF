from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import cm
import os

def creer_pdf(nom_fichier, nom_projet="", localisation="", total_paye="", date_paiement="", etat_projet="", details_facturation=None):
    # Obtenir le chemin absolu du dossier courant
    chemin_courant = os.path.dirname(os.path.abspath(__file__))
    # Construire le chemin vers le logo dans le dossier assets
    logo_path = os.path.join(chemin_courant, "assets", "logo.png")
    
    # Créer un nouveau PDF avec la taille A4
    c = canvas.Canvas(nom_fichier, pagesize=A4)
    
    # Ajouter le logo
    try:
        if os.path.exists(logo_path):
            width, height = A4
            
            # Ajuster les dimensions et la position du logo
            logo_width = 80  # Réduit de 100 à 80
            logo_height = 80  # Réduit de 100 à 80
            margin = 40
            
            # Position en haut à gauche
            x = margin
            y = height - logo_height - margin
            
            c.drawImage(logo_path, x, y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
        else:
            print(f"Le fichier logo n'a pas été trouvé à l'emplacement : {logo_path}")
    except Exception as e:
        print(f"Erreur lors de l'ajout du logo: {e}")
    
    # Ajuster la position du titre (plus haut)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(160, height - 70, "Mes Rémunérations")
    
    # Ajuster la position du sous-titre
    c.setFont("Helvetica", 12)
    c.drawString(160, height - 100, "Vous trouverez ci-dessous les rémunérations de votre projet")
    
    # Ajuster la position de la ligne horizontale
    ligne_y = height - 120  # Position plus haute pour la ligne
    c.line(margin, ligne_y, width - margin, ligne_y)
    
    # Ajuster la position du paragraphe
    texte = """Vous trouverez ci-dessous les détails de rémunérations de votre projet."""
    y = ligne_y - 30  # Espacement après la ligne
    
    for ligne in texte.splitlines():
        c.drawString(margin, y, ligne)
        y -= 15
    
    # Après le paragraphe initial, ajout des informations du projet
    width, height = A4
    margin = 40
    
    # Position de départ pour les informations du projet
    info_start_y = ligne_y - 80  # Espace après le paragraphe d'introduction
    
    # Style pour les labels
    c.setFont("Helvetica-Bold", 11)
    label_x = margin
    value_x = margin + 150  # Décalage pour les valeurs
    
    # Style pour les valeurs
    c.setFont("Helvetica", 11)
    
    # Fonction helper pour ajouter une ligne d'information
    def ajouter_info(label, valeur, y_pos):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(label_x, y_pos, label)
        c.setFont("Helvetica", 11)
        c.drawString(value_x, y_pos, valeur)
        return y_pos - 25  # Espacement entre les lignes
    
    # Dessiner un rectangle pour encadrer les informations
    box_padding = 15
    box_top = info_start_y + box_padding
    box_height = 150  # Hauteur ajustée pour contenir toutes les informations
    c.rect(margin - 10, box_top - box_height, width - 2 * margin + 20, box_height + 20)
    
    # Ajouter les informations du projet
    current_y = info_start_y
    current_y = ajouter_info("Nom du Projet:", nom_projet, current_y)
    current_y = ajouter_info("Localisation:", localisation, current_y)
    current_y = ajouter_info("Total Payé:", total_paye, current_y)
    current_y = ajouter_info("Date de Paiement:", date_paiement, current_y)
    current_y = ajouter_info("État du Projet:", etat_projet, current_y)
    
    # Ajouter une ligne de séparation après les informations
    c.line(margin, current_y - 20, width - margin, current_y - 20)
    
    # Si aucun détail de facturation n'est fourni, utiliser des données d'exemple
    if details_facturation is None:
        details_facturation = [
            ["Description", "Quantité", "Prix unitaire", "Total"],
            ["Développement Frontend", "80h", "75 €/h", "6 000 €"],
            ["Développement Backend", "120h", "85 €/h", "10 200 €"],
            ["Design UI/UX", "40h", "65 €/h", "2 600 €"],
        ]
    
    # Ajouter la table de facturation
    def ajouter_table_facturation(canvas, details, start_y):
        # Style de la table
        style = TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Corps de la table
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Centrer les chiffres
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),     # Aligner le texte à gauche
            
            # Bordures
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            
            # Espacement
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        # Calculer les largeurs des colonnes
        width, height = A4
        col_widths = [width * 0.35, width * 0.15, width * 0.2, width * 0.15]
        
        # Créer la table
        table = Table(details, colWidths=col_widths)
        table.setStyle(style)
        
        # Dessiner la table
        table.wrapOn(canvas, width, height)
        table.drawOn(canvas, margin, start_y - table._height - 40)
        
        return start_y - table._height - 60  # Retourner la position Y après la table
    
    # Ajouter un titre pour la section facturation
    current_y = current_y - 40  # Espace après la section précédente
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Détails de la Facturation")
    
    # Ajouter la table
    final_y = ajouter_table_facturation(c, details_facturation, current_y)
    
    # Ajouter le total général
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - margin - 200, final_y, "Total Général:")
    c.drawString(width - margin - 80, final_y, total_paye)
    
    c.save()

# Exemple d'utilisation avec des détails de facturation
details_exemple = [
    ["Description", "Quantité", "Prix unitaire", "Total"],
    ["Analyse des besoins", "20h", "90 €/h", "1 800 €"],
    ["Développement", "150h", "85 €/h", "12 750 €"],
    ["Tests et déploiement", "30h", "75 €/h", "2 250 €"],
    ["Formation", "8h", "120 €/h", "960 €"],
]

creer_pdf(
    "mes_remunerations.pdf",
    nom_projet="Développement Site E-commerce",
    localisation="Paris, France",
    total_paye="17 760 €",
    date_paiement="15 Mars 2024",
    etat_projet="En cours",
    details_facturation=details_exemple
)