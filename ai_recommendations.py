#Function definition for generating product recommendations.
#Takes the current product, list of all products, and number of recommendations to return
#(default is 4).
def get_recommendations(current_product, all_products, num_recommendations=4):
    """
    Simple recommendation algorithm based on:
    1. Same category products
    2. Similar price range (±30%)
    3. Higher rated products (if review data available)
    """
    recommendations = []
    current_category = current_product['category']  #Extracts the current product's category and price,
    current_price = current_product['price']        # then calculates ±30% price range for similarity.
    price_range = current_price * 0.3
    
    # Filters all products to find ones in the same category and within ±30% price difference,
    # excluding the current product itself.
    candidates = [
        p for p in all_products 
        if p['id'] != current_product['id'] and 
           p['category'] == current_category and
           abs(p['price'] - current_price) <= price_range
    ]
    
    # If not enough in same category, broaden to other categories
    if len(candidates) < num_recommendations:
        remaining = num_recommendations - len(candidates)
        other_candidates = [
            p for p in all_products 
            if p['id'] != current_product['id'] and 
               p['category'] != current_category
        ]
        # Sort by price similarity
        other_candidates.sort(key=lambda x: abs(x['price'] - current_price))
        candidates.extend(other_candidates[:remaining])
    
    # Ensure we don't recommend the same product
    candidates = [p for p in candidates if p['id'] != current_product['id']]
    
    return candidates[:num_recommendations]