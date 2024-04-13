import requests
from bs4 import BeautifulSoup
import csv

additional_links = [
    "https://verify-sy.com/list/16/%D8%A7%D8%AD%D8%AA%D9%8A%D8%A7%D9%84",
    "https://verify-sy.com/all/53/%D8%AA%D8%B6%D9%84%D9%8A%D9%84",
    "https://verify-sy.com/all/54/%D9%86%D8%B8%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D9%85%D8%A4%D8%A7%D9%85%D8%B1%D8%A9",
    "https://verify-sy.com/all/55/%D9%83%D8%B0%D8%A8-%D8%A8%D8%A7%D8%B3%D9%85-%D8%A7%D9%84%D8%B9%D9%84%D9%85",
    "https://verify-sy.com/all/56/%D8%AE%D8%B7%D8%A3",
    "https://verify-sy.com/all/57/%D8%A7%D9%86%D8%AD%D9%8A%D8%A7%D8%B2",
    "https://verify-sy.com/all/58/%D8%AA%D9%84%D8%A7%D8%B9%D8%A8-%D8%A8%D8%A7%D9%84%D8%AD%D9%82%D8%A7%D8%A6%D9%82",
    "https://verify-sy.com/all/59/%D8%B9%D9%86%D9%88%D8%A7%D9%86-%D9%85%D8%B6%D9%84%D9%84",
    "https://verify-sy.com/all/60/%D8%B3%D8%AE%D8%B1%D9%8A%D8%A9",
    "https://verify-sy.com/all/61/%D8%AE%D8%A7%D8%B1%D8%AC-%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D9%82",
    "https://verify-sy.com/all/62/%D8%BA%D9%8A%D8%B1-%D9%85%D8%A4%D9%83%D8%AF",
    "https://verify-sy.com/all/115/%D9%86%D8%A7%D9%81%D8%B0%D8%A9-%D8%A5%D9%84%D9%89-%D8%AA%D8%A3%D9%83%D8%AF",
    "https://verify-sy.com/all/116/%D9%86%D8%A7%D9%81%D8%B0%D8%A9-%D8%A5%D9%84%D9%89-%D8%A7%D9%84%D8%B9%D8%A7%D9%84%D9%85",
    "https://verify-sy.com/all/165/%D9%85%D8%A4%D9%83%D8%AF"
]

def scrap_norumors_page():
    page = requests.get("http://norumors.net/")
    articles_details = []

    if page.status_code == 200:
        src = page.content
        soup = BeautifulSoup(src, "lxml")

        articles = soup.find_all('div', {'class': 'rumor__meta'})

        for article in articles:
            titre = article.find('h2').text.strip()
            domaine = article.find('li').text.strip()
            articles_details.append({'titre': titre, 'domaine': domaine, 'type_news': 'اشاعة'})

        print("Les données de Norumors ont été récupérées.")

    else:
        print("La requête a échoué pour Norumors avec le code de statut:", page.status_code)

    return articles_details

def scrap_fatabyyano_pages():
    articles_details = []

    for page_number in range(1, 178):
        page_url = f"https://fatabyyano.net/page/{page_number}/"
        try:
            page = requests.get(page_url)
            page.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            src = page.content
            soup = BeautifulSoup(src, "html.parser")

            articles = soup.find_all('h2', {'class': 'w-post-elm post_title usg_post_title_1 has_text_color entry-title color_link_inherit'})

            for article in articles:
                titre = article.text.strip()
                domaine = ""
                type_news_element = article.find_next('span', {'class': 'w-btn-label'})
                if type_news_element:
                    type_news = type_news_element.text.strip()
                    if type_news == "تحميل المزيد من الأخبار":
                        type_news = ""
                else:
                    type_news = "N/A"
                
                articles_details.append({'titre': titre, 'domaine': domaine, 'type_news': type_news})

            print(f"Page {page_number} traitée.")

        except requests.exceptions.RequestException as e:
            print(f"La requête a échoué pour la page {page_number} avec l'erreur : {e}")

    print("Les données de Fatabyyano ont été récupérées.")

    return articles_details


def extract_data_from_additional_links():
    with open('articles.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['titre', 'domaine', 'type_news']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for link in additional_links:
            page = requests.get(link)
            if page.status_code == 200:
                src = page.content
                soup = BeautifulSoup(src, "lxml")
                
                # Trouver tous les articles sur la page
                articles = soup.find_all('div', {'class': 'list_description'})
                types_news = soup.find_all('div', {'class': 'blog_author_data'})

                for article, type_news in zip(articles, types_news):
                    titre = article.find('h3').text.strip()
                    type_news_text = type_news.find('a').text.strip().split()[0]
                    writer.writerow({'titre': titre, 'domaine': '', 'type_news': type_news_text})

                print(f"Data from {link} has been written to 'articles.csv'")
            else:
                print(f"Request failed for {link} with status code: {page.status_code}")

def main():
    articles_norumors = scrap_norumors_page()
    articles_fatabyyano = scrap_fatabyyano_pages()

    extract_data_from_additional_links()

    # Combine all articles into one list
    all_articles = articles_norumors + articles_fatabyyano

    # Initialize dictionaries to store counts
    domaine_counts = {}
    type_news_counts = {}

    # Write all articles to CSV
    with open('articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['titre', 'domaine', 'type_news']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in all_articles:
            writer.writerow(article)

            # Count articles in each domaine
            domaine = article['domaine']
            domaine_counts[domaine] = domaine_counts.get(domaine, 0) + 1

            # Count articles with specific type_news
            type_news = article['type_news']
            type_news_counts[type_news] = type_news_counts.get(type_news, 0) + 1

    print("All data has been collected and written to 'articles.csv'.")

    # Print counts
    print("Nombre d'articles dans chaque domaine :")
    for domaine, count in domaine_counts.items():
        print(f"{domaine}: {count}")

    print("\nNombre d'articles avec chaque type de news :")
    for type_news, count in type_news_counts.items():
        print(f"{type_news}: {count}")

if __name__ == "__main__":
    main()
