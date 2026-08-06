"""
Script to add interpretation markdown cells to lab9.ipynb.
Replaces the 'Summarize your observations' placeholder with SVM observations,
and inserts interpretation cells after PCA and LDA sections.
"""
import json
import uuid

NOTEBOOK_PATH = r"d:\Projects\MCA-Lab\Sem4\ML\ML-Lab-2547160\Lab9\lab9.ipynb"

def make_md_cell(source_lines):
    """Create a markdown cell dict with the given source lines."""
    return {
        "cell_type": "markdown",
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "source": source_lines
    }

def main():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb["cells"]

    # ── 1. Replace "Summarize your observations" with SVM interpretation ──
    svm_interpretation = [
        "### **Observations & Interpretation — SVM Classification (Breast Cancer Dataset)**\n",
        "\n",
        "**1. Data Preprocessing**\n",
        "- The Breast Cancer dataset contains **569 samples** with **30 numerical features** describing cell nuclei characteristics (radius, texture, perimeter, area, smoothness, etc.).\n",
        "- The target variable maps Malignant → `0` and Benign → `1`, creating a binary classification task.\n",
        "- **StandardScaler** was applied to standardize all features to zero mean and unit variance. This is critical for SVM because the algorithm relies on distance-based margin optimization — features with larger scales would otherwise dominate.\n",
        "\n",
        "**2. Model Training & Hyperparameter Tuning**\n",
        "- A baseline **Linear SVM** with default `C=1.0` was first evaluated.\n",
        "- **GridSearchCV** exhaustively searched over `C ∈ {0.01, 0.1, 1, 10, 100}`, `kernel ∈ {'linear', 'rbf', 'poly'}`, and `gamma ∈ {'scale', 'auto'}` using 5-fold cross-validation.\n",
        "- The optimal configuration found was **`C=0.1, kernel='linear', gamma='scale'`**, indicating that the classes are **linearly separable** in the standardized feature space.\n",
        "- The lower `C` value (0.1 vs. default 1.0) implies a **wider soft margin**, which improves generalization and reduces overfitting.\n",
        "\n",
        "**3. Evaluation Metrics**\n",
        "- **Accuracy ≈ 98.25%** — Only ~2 misclassified samples out of 114 test cases.\n",
        "- **Precision ≈ 98.61%** — When the model predicts Benign, it is almost always correct.\n",
        "- **Recall ≈ 98.61%** — The model successfully identifies the vast majority of true Benign cases.\n",
        "- **F1‑Score ≈ 98.61%** — Demonstrates an excellent balance between precision and recall.\n",
        "\n",
        "**4. Confusion Matrix Insights**\n",
        "- The confusion matrix shows very few misclassifications in either direction.\n",
        "- In a clinical context, **False Negatives** (malignant tumors classified as benign) are the most dangerous errors as they delay treatment. The model's high recall for the Malignant class (~97.6%) confirms its reliability as a diagnostic support tool.\n",
        "\n",
        "**5. Key Takeaway**\n",
        "- SVM with proper feature scaling and hyperparameter tuning achieves **near-perfect classification** on the Breast Cancer dataset, demonstrating its effectiveness for high-dimensional binary classification tasks in medical diagnostics."
    ]

    svm_replaced = False
    for i, cell in enumerate(cells):
        if cell.get("cell_type") == "markdown":
            src = "".join(cell.get("source", []))
            if "Summarize your observations" in src:
                cells[i] = make_md_cell(svm_interpretation)
                svm_replaced = True
                print(f"[OK] Replaced SVM observations placeholder at cell index {i}")
                break

    if not svm_replaced:
        print("[WARN] Could not find 'Summarize your observations' cell — skipping SVM.")

    # ── 2. Insert PCA interpretation after the last PCA code cell (loadings cell) ──
    pca_interpretation = [
        "### **Observations & Interpretation — PCA (Wine Dataset)**\n",
        "\n",
        "**1. Dataset Overview**\n",
        "- The **Wine dataset** (from `sklearn.datasets.load_wine`) contains **178 samples** across **3 cultivar classes** (class_0, class_1, class_2) and **13 chemical features** (alcohol, malic_acid, ash, etc.).\n",
        "- All features were standardized using `StandardScaler` before applying PCA, ensuring each feature contributes equally to the variance computation.\n",
        "\n",
        "**2. Dimensionality Reduction**\n",
        "- PCA with `n_components=2` reduced the original **13-dimensional** feature space down to **2 principal components**.\n",
        "- The shape of the transformed data is `(178, 2)` — each sample is now represented by just 2 values.\n",
        "\n",
        "**3. Explained Variance**\n",
        "- **PC1** captures approximately **36.2%** of total variance, and **PC2** captures approximately **19.2%**.\n",
        "- Together, the first 2 components retain roughly **55.4%** of the total variance — meaning we lose about 44.6% of information, but gain a 2D visualization.\n",
        "\n",
        "**4. PCA Scatter Plot Analysis**\n",
        "- The 2D scatter plot shows **moderate but imperfect class separation**:\n",
        "  - *class_0* (top-right region) is relatively well-separated from the other two classes.\n",
        "  - *class_1* and *class_2* show significant **overlap** in the PCA-projected space.\n",
        "- This overlap occurs because PCA is an **unsupervised** technique — it maximizes overall variance without considering class labels.\n",
        "\n",
        "**5. Feature Loadings (Top Drivers)**\n",
        "- **PC1** is most strongly influenced by: `flavanoids`, `total_phenols`, `od280/od315_of_diluted_wines` — all phenolic compound measurements.\n",
        "- **PC2** is most strongly influenced by: `color_intensity`, `alcohol`, `proline` — features related to color and alcohol content.\n",
        "- This reveals that the primary axis of variation in wine data relates to **phenolic chemistry**, while the secondary axis relates to **color and alcohol properties**.\n",
        "\n",
        "**6. Comparison Table**\n",
        "- The comparison table confirms:\n",
        "  - Feature count reduced from **13 → 2** (84.6% reduction).\n",
        "  - Variance retained: **55.4%** — a trade-off between simplicity and information loss.\n",
        "  - Computational cost: significantly **lower** for downstream tasks.\n",
        "\n",
        "**7. Key Takeaway**\n",
        "- PCA is effective for **exploratory visualization** and **dimensionality reduction**, but since it is unsupervised, it does not optimize for class separability. For classification-oriented dimensionality reduction, **LDA** (covered next) is more appropriate."
    ]

    # Find the loadings cell (contains "loadings = pd.DataFrame(pca.components_")
    pca_inserted = False
    for i, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            if "loadings = pd.DataFrame(pca.components_" in src:
                cells.insert(i + 1, make_md_cell(pca_interpretation))
                pca_inserted = True
                print(f"[OK] Inserted PCA interpretation after cell index {i}")
                break

    if not pca_inserted:
        print("[WARN] Could not find PCA loadings cell — skipping PCA interpretation.")

    # ── 3. Insert LDA + comparison interpretation after the last code cell (PCA vs LDA plot) ──
    lda_interpretation = [
        "### **Observations & Interpretation — LDA & PCA vs LDA Comparison**\n",
        "\n",
        "**1. LDA Transformation**\n",
        "- **Linear Discriminant Analysis (LDA)** with `n_components=2` was applied to the same standardized Wine dataset.\n",
        "- Unlike PCA, LDA is a **supervised** technique — it uses class labels (`y_wine`) during `fit_transform` to find projections that **maximize between-class separation** while **minimizing within-class variance**.\n",
        "- The transformed data has shape `(178, 2)`, same as PCA.\n",
        "\n",
        "**2. Explained Variance Ratio (LDA)**\n",
        "- **LD1** captures approximately **68.7%** of the discriminant information, and **LD2** captures approximately **31.3%**.\n",
        "- Together, the 2 linear discriminants capture **100%** of the between-class discriminant information (since there are 3 classes, LDA can produce at most `k-1 = 2` discriminant components).\n",
        "\n",
        "**3. LDA Scatter Plot Analysis**\n",
        "- The 2D LDA scatter plot shows **dramatically better class separation** compared to PCA:\n",
        "  - All three cultivar classes (*class_0*, *class_1*, *class_2*) form **tight, well-separated clusters** with virtually **no overlap**.\n",
        "  - The inter-class distances are large and clear along both LD1 and LD2 axes.\n",
        "- This superior separation is a direct result of LDA's supervised optimization objective.\n",
        "\n",
        "**4. PCA vs LDA Side-by-Side Comparison**\n",
        "- The side-by-side plot visually confirms the key difference:\n",
        "  - **PCA** (left panel): Classes overlap, especially class_1 and class_2. PCA finds directions of maximum *overall* variance, which may not align with class boundaries.\n",
        "  - **LDA** (right panel): Classes are cleanly separated. LDA finds directions that are *most discriminative* for classification.\n",
        "\n",
        "**5. When to Use Each Technique**\n",
        "\n",
        "| Criterion | PCA | LDA |\n",
        "|---|---|---|\n",
        "| **Type** | Unsupervised | Supervised |\n",
        "| **Objective** | Maximize total variance | Maximize class separability |\n",
        "| **Requires labels?** | No | Yes |\n",
        "| **Max components** | min(n_features, n_samples) | n_classes − 1 |\n",
        "| **Best for** | Exploratory analysis, noise reduction | Classification preprocessing |\n",
        "\n",
        "**6. Key Takeaway**\n",
        "- When labeled data is available and the goal is **classification**, LDA consistently outperforms PCA for dimensionality reduction because it directly optimizes for class separability.\n",
        "- PCA remains valuable when labels are unavailable, or when the goal is general-purpose dimensionality reduction (e.g., for visualization or denoising).\n",
        "- On the Wine dataset, LDA with just 2 components achieves **near-perfect class separation**, making it an ideal preprocessing step before applying classifiers."
    ]

    # Find the last code cell (PCA vs LDA side-by-side plot)
    lda_inserted = False
    for i in range(len(cells) - 1, -1, -1):
        cell = cells[i]
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            if "PCA vs LDA" in src or "axes[0]" in src:
                cells.insert(i + 1, make_md_cell(lda_interpretation))
                lda_inserted = True
                print(f"[OK] Inserted LDA/comparison interpretation after cell index {i}")
                break

    if not lda_inserted:
        print("[WARN] Could not find PCA vs LDA comparison cell — skipping LDA interpretation.")

    # ── Save ──
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print("\n[DONE] Notebook updated successfully.")

if __name__ == "__main__":
    main()
