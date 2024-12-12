import mysql.connector
from datetime import datetime
from writePPDF import creer_pdf
def get_project_data(project_id):
    try:
        # Configuration de la connexion à la base de données
        connection = mysql.connector.connect(
            host="localhost",
            user="votre_utilisateur",
            password="votre_mot_de_passe",
            database="votre_base_de_donnees"
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Requête modifiée pour correspondre à votre structure
        project_query = """
        SELECT 
            p.project_name as nom_projet,
            p.location as localisation,
            py.amount_paid as total_paye,
            py.payment_date as date_paiement,
            p.project_status as etat_projet
        FROM PROJECTS p
        LEFT JOIN PAYMENTS py ON py.project_id = p.id
        WHERE p.id = %s
        """
        cursor.execute(project_query, (project_id,))
        project_info = cursor.fetchone()
        
        # Requête pour les détails des commissions
        details_query = """
        SELECT 
            CONCAT(u.first_name, ' ', u.last_name) as description,
            t.team_name as equipe,
            c.amount as montant_commission,
            py.amount_paid as montant_paye
        FROM COMMISSIONS c
        JOIN TEAMS t ON t.id = c.team_id
        JOIN USERS u ON u.id = c.user_id
        JOIN PAYMENTS py ON py.commission_id = c.id
        WHERE py.project_id = %s
        """
        cursor.execute(details_query, (project_id,))
        commission_details = cursor.fetchall()
        
        # Formater les détails pour le PDF
        details_table = [["Consultant", "Équipe", "Commission", "Montant payé"]]
        for detail in commission_details:
            details_table.append([
                detail['description'],
                detail['equipe'],
                f"{detail['montant_commission']} €",
                f"{detail['montant_paye']} €"
            ])
        
        return project_info, details_table
        
    except mysql.connector.Error as err:
        print(f"Erreur SQL: {err}")
        return None, None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def generer_pdf_from_db(project_id, output_filename):
    # Récupérer les données de la base de données
    project_info, details_facturation = get_project_data(project_id)
    
    if project_info and details_facturation:
        # Formater la date pour l'affichage
        date_paiement = project_info['date_paiement'].strftime("%d %B %Y") if project_info['date_paiement'] else ""
        
        # Générer le PDF avec les données récupérées
        creer_pdf(
            nom_fichier=output_filename,
            nom_projet=project_info['nom_projet'],
            localisation=project_info['localisation'],
            total_paye=f"{project_info['total_paye']} €",
            date_paiement=date_paiement,
            etat_projet=project_info['etat_projet'],
            details_facturation=details_facturation
        )
        return True
    return False

# Exemple d'utilisation
if __name__ == "__main__":
    project_id = 1  # ID du projet à générer
    output_file = f"facture_projet_{project_id}.pdf"
    
    if generer_pdf_from_db(project_id, output_file):
        print(f"PDF généré avec succès: {output_file}")
    else:
        print("Erreur lors de la génération du PDF")