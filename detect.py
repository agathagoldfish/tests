import os
import argparse
from tqdm import tqdm
import pandas as pd
from utils import MANIPULATION_TYPES, get_all_manipulation_types, detect_matches
import matplotlib.pyplot as plt
import seaborn as sns

def save_visualization(df, output_path):
    manipulation_types = [col for col in df.columns if col not in ['image_id', 'method', 'avg_score']]
    
    # 1. Bar chart of average match scores
    avg_scores = df[manipulation_types].mean().sort_values()
    plt.figure(figsize=(10,6))
    sns.barplot(x=avg_scores.index, y=avg_scores.values, palette='viridis')
    plt.ylabel("Average Similarity Score")
    plt.title("Average pHash Similarity by Manipulation Type")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "average_scores_bar.png"))
    plt.close()
    
    # 2. Heatmap of scores per image
    plt.figure(figsize=(12,8))
    sns.heatmap(df[manipulation_types], cmap='viridis', annot=False)
    plt.ylabel("Image Index")
    plt.xlabel("Manipulation Type")
    plt.title("pHash Similarity Heatmap (Images x Manipulations)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "similarity_heatmap.png"))
    plt.close()
    
    # 3. Boxplot of score distribution per manipulation
    plt.figure(figsize=(12,6))
    sns.boxplot(data=df[manipulation_types], palette='magma')
    plt.ylabel("Similarity Score")
    plt.title("pHash Score Distribution per Manipulation Type")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "scores_boxplot.png"))
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Detect image matches using pHash')
    parser.add_argument('--originals', type=str, default='originals', help='Path to original images')
    parser.add_argument('--manipulated', type=str, default='manipulated', help='Path to manipulated images')
    parser.add_argument('--output', type=str, default='results', help='Path to output directory')
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    original_files = sorted([f for f in os.listdir(args.originals) if f.lower().endswith(('.jpg','.jpeg','.png'))])
    manipulation_types = get_all_manipulation_types()
    
    results = {manip_name: [] for manip_name in manipulation_types}
    results['image_id'] = []
    
    print(f"Processing {len(original_files)} images with pHash...")
    
    for orig_file in tqdm(original_files):
        orig_path = os.path.join(args.originals, orig_file)
        image_id = os.path.splitext(orig_file)[0]
        results['image_id'].append(image_id)
        
        for letter, manip_name in MANIPULATION_TYPES.items():
            manip_file = f"{image_id}{letter}.jpg"
            manip_path = os.path.join(args.manipulated, manip_file)
            
            if not os.path.exists(manip_path):
                results[manip_name].append(0)
                continue
            
            score = detect_matches(orig_path, manip_path, method='phash')
            results[manip_name].append(score)
    
    df = pd.DataFrame(results)
    df['method'] = 'phash'
    df['avg_score'] = df[manipulation_types].mean(axis=1)
    
    # Average scores and hardest manipulation
    avg_scores = {manip_name: df[manip_name].mean() for manip_name in manipulation_types}
    hardest_manip = min(avg_scores, key=avg_scores.get)
    hardest_score = avg_scores[hardest_manip]
    
    # Save CSV and summary
    results_file = os.path.join(args.output, 'phash_results.csv')
    df.to_csv(results_file, index=False)
    
    summary_file = os.path.join(args.output, 'phash_summary.txt')
    with open(summary_file, 'w') as f:
        f.write("Image Matching Results using pHash\n")
        f.write("="*50 + "\n\n")
        f.write("Average Match Scores by Manipulation Type:\n")
        f.write("-"*40 + "\n")
        for manip, score in sorted(avg_scores.items(), key=lambda x: x[1]):
            f.write(f"{manip:15}: {score:.2f}\n")
        f.write("\n" + "="*50 + "\n")
        f.write(f"HARDEST MANIPULATION TECHNIQUE: {hardest_manip}\n")
        f.write(f"Average Match Score: {hardest_score:.2f}\n")
        f.write("="*50 + "\n")
    
    # Visualization
    save_visualization(df, args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY FOR pHash")
    print("="*60)
    for manip, score in sorted(avg_scores.items(), key=lambda x: x[1]):
        print(f"{manip:15}: {score:.2f}")
    print("\n" + "="*60)
    print(f"HARDEST MANIPULATION TECHNIQUE: {hardest_manip}")
    print(f"Average Match Score: {hardest_score:.2f}")
    print("="*60)
    
    print(f"\nResults saved to: {results_file}")
    print(f"Summary saved to: {summary_file}")
    print(f"Visualizations saved to: {args.output}")

if __name__ == "__main__":
    main()
