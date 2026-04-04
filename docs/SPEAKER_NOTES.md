# EPA Presentation - Speaker Notes

## Suggested Structure (20-30 min, 2 speakers)

```
Speaker 1 (~12-15 min): Slides 1-10
  - Title, Agenda, Problem, Background, All Augmentations

Speaker 2 (~12-15 min): Slides 11-18+
  - Architecture, Models, Datasets, Results, Conclusion, Future Work, Q&A
```

---

## SLIDE 1: Title Slide

**EPA: Enhanced Protein Augmentation — A Benchmark Framework for Protein Data Augmentation Strategies**

> No speaking needed beyond a quick intro. Name yourselves, your course, and move on.

---

## SLIDE 2: Agenda

> "We'll walk through why protein augmentation matters, explain every augmentation technique we implemented, show you how our framework works, and end with results. [Speaker 1] will cover the problem and all the augmentation methods. [Speaker 2] will take over for the architecture, models, results, and conclusion."

---

## SLIDE 3: Problem Statement & Motivation

### Speaker Notes:

> "Let's start with the core problem. In computational biology, we want to predict things about proteins — where they localize in a cell, whether they're soluble, how they interact with other proteins. The challenge is that labeled protein data is extremely scarce compared to, say, image or text data.
>
> Why? Because labeling proteins requires wet-lab experiments — you physically have to go into a lab, express the protein, run assays. That takes weeks to months and costs significant money per data point.
>
> So we end up with small datasets — often just a few thousand samples. But the space of possible proteins is astronomically large. A protein of length 300 has 20^300 possible sequences. Our training data covers a vanishingly small fraction of that.
>
> The result? Models overfit. They memorize the training set instead of learning generalizable patterns. They fail on unseen protein families or even minor mutations.
>
> The solution we explore: **data augmentation** — artificially expanding the training data through transformations that preserve biological meaning while increasing diversity. This is the same idea that revolutionized computer vision (random crops, flips, color jitter), but adapted for protein sequences.
>
> Our goal: build a comprehensive benchmarking framework to systematically evaluate which augmentation strategies actually work for protein prediction tasks."

---

## SLIDE 4: Background — Proteins 101

### Speaker Notes:

> "Quick background for context. Proteins are linear chains of amino acids — there are 20 standard ones, each with a single-letter code. Think of a protein as a string over a 20-letter alphabet. Lengths range from ~50 residues for small peptides to 30,000+ for giant complexes like titin.
>
> The key insight: a protein's function is determined by its 3D structure, which in turn is determined by its amino acid sequence. So if we can predict properties from the sequence alone, that's hugely valuable — no need for expensive structure determination.
>
> The ML framing: given a sequence (string of letters), predict a property (class label, regression value, per-residue annotation). Standard supervised learning, except the datasets are tiny and the input space is vast.
>
> Our base paper is Sun et al. 2024 — 'Enhancing Protein Predictive Models via Proteins Data Augmentation: A Benchmark and New Directions.' They were the first to systematically benchmark augmentation for protein ML. We implement their techniques plus five additional ones from other papers."

---

## SLIDE 5: Augmentation Overview — Three Levels

### Speaker Notes:

> "We implement 23 augmentation methods organized into three levels of increasing sophistication:
>
> **Token-level** (7 methods): These operate on individual amino acid residues. Think of them as character-level edits — insert a letter, delete a letter, swap two letters. Simple but effective as baselines.
>
> **Sequence-level** (8 methods): These operate on the structure of the sequence — cropping a segment, shuffling a region, reversing the whole thing, cutting and reassembling like shuffling a deck of cards.
>
> **Semantic-level** (8 methods): These are the interesting ones. They use actual biological domain knowledge — biochemical properties, codon tables, molecular interactions — to make augmentations that are biologically meaningful, not just random noise.
>
> Every single method follows the same interface: you give it a sequence and an intensity parameter between 0 and 1, and it returns an augmented sequence. This unified interface lets us mix and match them freely in our policy search."

---

## SLIDE 6: Token-Level Augmentations (7 methods)

### Speaker Notes:

> "Let me walk through each token-level method.
>
> **1. Random Insert** — Pick random positions in the sequence and insert a random amino acid. If your protein is METHYL, you might get MKETHWYL. The intensity parameter controls what fraction of the sequence length gets inserted. This increases sequence length and adds noise, simulating insertion mutations that occur in nature.
>
> **2. Random Substitute** — Pick random positions and replace the amino acid with a completely random one from the 20 standard amino acids. METHYL might become MDTHWL. This is the most aggressive token-level augmentation because the replacement has no relationship to the original — you could replace a tiny hydrophobic alanine with a bulky charged arginine.
>
> **3. Random Swap** — Pick two random positions and swap them. METHYL becomes MEHTYL if you swap T and H. This preserves the amino acid composition (same letters, different order) but disrupts local patterns.
>
> **4. Random Delete** — Each position has a probability `m` of being deleted. METHYL might become MTHL. This simulates deletion mutations. We guarantee at least one residue survives so we never get an empty sequence.
>
> **5. Mask Residues (MLM-style)** — This is directly inspired by BERT and its protein variants like ProtBERT and ESM. We select positions to mask, then: 80% of the time replace with a mask token 'X', 10% replace with a random amino acid, 10% leave unchanged. This is exactly the masking strategy from the original BERT paper. The model learns to be robust to missing information.
>
> **6. Conservative Mask** — Same idea as masking, but instead of replacing with 'X' or random, we replace with a biochemically *similar* amino acid. So glutamic acid (E) becomes aspartic acid (D) — both are negatively charged. Leucine (L) becomes isoleucine (I) — both are large hydrophobic. This is much gentler than random masking because the replacement preserves the biochemical character of that position.
>
> **7. Conservative Substitute** — Like random substitute, but restricted to biochemically similar amino acids. We define groups: hydrophobic aliphatics (A, V, I, L, M), aromatics (F, Y, W), positively charged (K, R, H), negatively charged (D, E), polar uncharged (S, T, N, Q), and so on. Substitutions only happen within a group. This mimics conservative mutations in evolution — the kind that are most likely to preserve protein function."

---

## SLIDE 7: Sequence-Level Augmentations (8 methods)

### Speaker Notes:

> "Now sequence-level — these rearrange the structure of the sequence.
>
> **8. Random Crop** — Extract a contiguous subsequence. If your protein is 100 residues and the intensity is 0.6, you get a 60-residue window starting at a random position. This forces the model to learn from partial sequences, like how random crops in image augmentation force learning from partial views.
>
> **9. Random Shuffle** — Pick a segment of the sequence (controlled by intensity) and shuffle the residues within it. The rest stays untouched. So positions 20-30 might get randomly permuted while 1-19 and 31-100 stay the same. This disrupts local patterns while preserving global structure.
>
> **10. Global Reverse** — Simply reverse the entire sequence. METHYL becomes LYHTHEM. This is a binary operation — the intensity parameter is ignored. It tests whether models are sensitive to sequence direction. Interestingly, some protein properties are direction-independent (like amino acid composition), so this can be a useful augmentation for those tasks.
>
> **11. Random Cut** — Cut the sequence at random points into segments, then shuffle the segments and reassemble. Like cutting a deck of cards. METH|YLA|MINE might become MINE|METH|YLA. This preserves all the local motifs but changes their relative positions.
>
> **12. Random Subsequence** — Similar to random cut, but after cutting into segments, we only keep a random subset. Some segments get dropped. This combines the effects of cropping and rearrangement.
>
> **13. Repeat Expansion** — Searches for tandem repeats in the sequence (like ABAB) and duplicates one copy. METHABAB becomes METHABABAB. Many real proteins have repeat regions, so this augmentation has biological grounding.
>
> **14. Repeat Contraction** — The opposite: finds tandem repeats and removes one copy. METHABABCD becomes METHABCD. Together with expansion, these model the repeat expansion/contraction mutations that are common in protein evolution.
>
> **15. Back-Translation Substitute** — This is clever. We translate the amino acid sequence to mRNA codons (each amino acid maps to a 3-nucleotide codon), then mutate random nucleotides, then translate back to amino acids. If a nucleotide mutation hits a codon and changes the encoded amino acid, we get a substitution. If it would create a stop codon, we reject it. This mimics how point mutations actually work at the DNA level — some positions in a codon are more tolerant to mutation than others."

---

## SLIDE 8: Semantic-Level — NTA (Nucleotide Augmentation)

### Speaker Notes:

> "Now the semantic-level methods. These are the most sophisticated because they use actual biological knowledge.
>
> **16. NTA (Nucleotide Augmentation)** — From Minot & Reddy 2022. This exploits a fundamental property of the genetic code: **codon degeneracy**. There are 64 possible 3-nucleotide codons but only 20 amino acids, so most amino acids are encoded by multiple codons. Alanine has 4 codons (GCT, GCC, GCA, GCG), Leucine has 6, Methionine has only 1.
>
> The process: take your amino acid sequence, back-translate each residue to a randomly chosen codon, then swap some codons for synonymous alternatives (different DNA, same amino acid), then forward-translate back. The result at the amino acid level is *identical* to the input.
>
> Wait — why is that useful if the protein sequence doesn't change? Because the *nucleotide representation* is different. If your model operates on nucleotide-level features (which some do), you get diversity. For amino-acid-level models, this augmentation has no effect, which is an important insight from our analysis.
>
> The original paper showed NTA improved performance on protein engineering tasks (GB1, AAV, Trastuzumab) by 2-6% accuracy."

---

## SLIDE 9: Semantic-Level — BootGen

### Speaker Notes:

> "**17. BootGen** — Adapted from a NeurIPS 2023 paper on bootstrapped generation for biological sequences.
>
> The key idea: don't just generate random augmented sequences — generate many candidates and *select the best one*. It's quality-controlled augmentation.
>
> The process:
> 1. **Generate candidates**: Create multiple variant sequences through conservative substitutions (replace amino acids with biochemically similar ones).
> 2. **Score each candidate** using a proxy quality function that measures:
>    - Amino acid composition similarity (40% weight) — does the augmented sequence have a similar distribution of amino acids?
>    - Biochemical property similarity (40% weight) — is the ratio of hydrophobic/polar/charged residues preserved?
>    - Length preservation (20% weight) — penalty if the sequence gets too long or short.
> 3. **Rank-based selection**: Use softmax over scores to probabilistically select a candidate. Higher-scored candidates are more likely to be chosen, but there's still randomness to maintain diversity. A temperature parameter controls this — lower temperature = more deterministic (pick the best), higher = more random.
>
> At low intensity, we generate 5 candidates with 1-2 substitutions. At high intensity, 20 candidates with up to 50% of positions modified. The proxy scoring ensures that even at high intensity, the output is biologically plausible."

---

## SLIDE 10: Semantic-Level — NaNa & MiGu

### Speaker Notes:

> "**18. NaNa (Novel Augmentation of New Node Attributes)** — From a paper on semantic augmentation for protein graph neural networks.
>
> The original NaNa works on protein structure graphs — it enriches node features with biophysical properties. We adapted it for sequence-level augmentation. The core idea: when substituting an amino acid, don't just use simple groups — use a *multi-dimensional similarity score* that considers:
>
> - **Hydrophobicity** (Kyte-Doolittle scale, 15% weight): Is this residue water-loving or water-fearing?
> - **Charge at pH 7.4** (25% weight): Is it positive, negative, or neutral? This is the most heavily weighted because charge is critical for protein folding and function.
> - **Van der Waals volume** (10% weight): How big is the side chain?
> - **Alpha-helix propensity** (20% weight, Chou-Fasman): How likely is this residue to be in a helix?
> - **Beta-sheet propensity** (20% weight): How likely to be in a sheet?
> - **Turn propensity** (10% weight): How likely to be in a turn/loop?
>
> For each position being augmented, we compute the similarity between the original amino acid and all 19 alternatives, then probabilistically select a replacement weighted by similarity. The higher the similarity threshold, the more conservative the substitution.
>
> **19. MiGu (Molecular Interactions and Geometric Upgrading)** — From the same paper, MiGu goes further than NaNa by considering *context*. It doesn't just look at the amino acid being replaced — it looks at the neighbors.
>
> Three critical interaction rules:
> 1. **Disulfide bond preservation**: If there's a cysteine (C) near another cysteine, keep it as cysteine. Disulfide bonds are structural anchors — breaking them could unfold the protein.
> 2. **Salt bridge preservation**: If a positively charged residue (K, R, H) is near a negatively charged one (D, E), maintain the charge. Salt bridges are crucial for stability.
> 3. **Aromatic cluster preservation**: If aromatic residues (F, W, Y, H) cluster together, keep them aromatic. Pi-stacking interactions stabilize protein cores.
>
> The process: analyze a k-mer window around each position, determine the dominant context type (hydrophobic, polar, charged, aromatic), then select substitution candidates that match that context. This makes MiGu much more biologically realistic than NaNa."

---

## SLIDE 11: Semantic-Level — RSA, PreIS, IMAEN, Spider

### Speaker Notes:

> "**20. RSA (Retrieved Sequence Augmentation)** — Inspired by Chang et al. 2023. The full RSA uses FAISS indexing to retrieve actual homologous sequences from databases like UniRef or Pfam — real proteins that are evolutionarily related to your query.
>
> Our simplified version simulates this by generating 'pseudo-homologs' through conservative mutations. The idea is the same: augment your training set with sequences that could plausibly exist in nature as evolutionary relatives. Low intensity = close homolog (just a few mutations), high intensity = distant homolog (many mutations). The variant `rsa_augment_with_original` has a 50% chance of returning the unchanged sequence, simulating the case where your database search finds an exact match.
>
> **21. PreIS (Supervised Data Augmentation)** — From a paper on influenza subtype prediction. The original PreIS does *cross-sequence mixing* — it takes two sequences with the same label and swaps segments between them. Our implementation is simplified to *self-mixing* within a single sequence because our framework's interface processes one sequence at a time.
>
> It does two things: (1) **Global segment swapping**: pick two non-overlapping segments and swap their positions, controlled by GAMMA_G=0.4. (2) **Local token shuffling**: randomly rearrange individual amino acids at selected positions, controlled by GAMMA_L=0.1. The key property: both operations preserve the exact amino acid composition — same letters, different arrangement. No new amino acids are introduced.
>
> **22. IMAEN (Interpretable Molecular Augmentation)** — Adapted from a drug-target interaction paper. The original IMAEN is actually a model architecture, not a data augmentation technique — its 'augmentation' refers to augmenting neighborhood information in a graph neural network. We extracted the *concept* of property-aware, interpretable augmentation.
>
> Our adaptation has three steps: (1) Select positions to modify based on amino acid properties — you can bias toward hydrophobic, polar, charged, or aromatic positions. (2) Apply conservative substitutions at those positions. (3) Add a small amount of controlled noise (10% of intensity). The 'interpretable' aspect is that you can trace exactly why each substitution was made.
>
> **23. Spider Augmentation** — From a paper on predicting spider neurotoxic peptides. This is the most straightforward semantic method: random substitution (50% of intensity) plus random insertion (50% of intensity). The original paper validated augmented sequences using BLAST against the original database — only sequences that had significant homology to real sequences were kept. We omit the BLAST step for speed, but the core augmentation logic is preserved."

---

## SLIDE 12: Framework Architecture — EPA Pipeline

*[Speaker 2 takes over here]*

### Speaker Notes:

> "Now let me walk you through how all these augmentations are actually used in our framework.
>
> EPA runs a **three-phase training pipeline**:
>
> **Phase 1 — Baseline Training**: We train the model with zero augmentation. This gives us a performance floor — how well does the model do with just the raw data? We save the best checkpoint based on validation accuracy.
>
> **Phase 2 — Policy Search**: This is where augmentation comes in. A 'policy' is a combination of augmentation operations. Specifically, a policy contains multiple 'sub-policies', and each sub-policy contains multiple operations. Each operation is a triple: (augmentation_name, probability, intensity_level).
>
> During training, for each sample, we randomly pick one sub-policy and apply its operations. Each operation fires with its probability — so if `random_crop` has probability 0.72, it runs 72% of the time. The intensity level controls how aggressive it is.
>
> We generate random policies and fine-tune the baseline model with each one for a few epochs. The policy that achieves the highest validation accuracy wins.
>
> **Phase 3 — Final Evaluation**: We report test set performance with the best augmentation policy.
>
> The entire system is configured via YAML files — model architecture, dataset paths, augmentation parameters, search budget — all externalized. No hardcoded values."

---

## SLIDE 13: Models

### Speaker Notes:

> "We benchmark across multiple model architectures to ensure our augmentation findings aren't model-specific.
>
> **LSTM (Bidirectional)**: Our workhorse model. ~500K parameters. The sequence is embedded (each amino acid to a 64-dim vector), passed through a bidirectional LSTM with 128 hidden units, then the final hidden states from both directions are concatenated and fed through fully connected layers with ReLU and dropout. Augmentation is applied *online* — each time a sample is loaded, it's augmented on-the-fly with probability 0.7. This means the model sees different augmented versions across epochs.
>
> **Random Forest**: A traditional ML baseline. We extract k-mer frequency features (k=3, so 8000 possible 3-mers) from each sequence and train a Random Forest classifier. Augmentation here is *offline* — we pre-augment the entire dataset before training, so the dataset physically gets larger. This is the only option since Random Forest can't do on-the-fly augmentation.
>
> **ResNet**: A 1D convolutional residual network. We treat the protein sequence like a 1D signal and apply residual convolution blocks. Currently experimental — we've had some import issues we're fixing.
>
> **ESM-2**: Planned but not yet implemented. This would be the most exciting — ESM-2 is a protein language model pre-trained on millions of sequences. Fine-tuning it with augmentation could push state-of-the-art results."

---

## SLIDE 14: Datasets

### Speaker Notes:

> "We evaluate across 8 datasets spanning 4 different task types:
>
> **Binary Classification**: Subcellular localization (2 classes — is this protein membrane-bound or soluble?), Solubility (will this protein stay dissolved or aggregate?). These are practically important questions in drug design.
>
> **Multi-class Classification**: Subcellular localization (10 classes — cytoplasm, nucleus, mitochondria, etc.), Remote homology (1,195 fold classes — which structural family does this protein belong to?). Remote homology is particularly challenging because the sequences can be very dissimilar even when the structures are similar.
>
> **Protein-Protein Interaction**: Yeast PPI and Human PPI — given two protein sequences, do they physically interact? This is a binary classification but on pairs of sequences.
>
> **Regression**: Beta-lactamase fitness — predict the continuous fitness value of beta-lactamase enzyme variants. Measured by Spearman correlation instead of accuracy.
>
> **Residue-level**: Secondary structure prediction — for each amino acid in the sequence, predict whether it's in an alpha-helix, beta-sheet, or coil. This is the only per-residue task.
>
> All datasets are stored in LMDB format with train/valid/test splits pre-defined."

---

## SLIDE 15: Results

### Speaker Notes:

> "Here are our benchmark results.
>
> For LSTM: subcellular localization 2-class reaches 89.3% accuracy, which is solid. The 10-class version drops to 69.1% — expected with more classes. Yeast PPI at 60.1% with MCC of 0.20 shows this is a harder task.
>
> For Random Forest: solubility at 77.0% is actually competitive, showing that sometimes simple models with good features work well. Beta-lactamase regression at 0.40 Spearman is modest but reasonable for a non-deep-learning model.
>
> **Key findings from our augmentation analysis**:
>
> First, **semantic augmentations consistently outperform random ones**. NaNa, MiGu, and RSA — the methods that respect biochemical properties — tend to help most. This makes intuitive sense: augmentations that preserve biological meaning create training examples the model can actually learn from, rather than noise.
>
> Second, **aggressive augmentations can hurt on small datasets**. Random substitute and random shuffle at high intensity often degrade performance because they create sequences that are too far from any real protein. The model wastes capacity learning from unrealistic examples.
>
> Third, **policy search finds task-specific combinations**. The optimal augmentation strategy for solubility prediction is different from the optimal one for remote homology. There's no single best augmentation — it depends on the task, the dataset size, and the model.
>
> Fourth, **online augmentation (LSTM) outperforms offline (Random Forest)** when using the same augmentation methods. Seeing different augmented versions each epoch is better than a fixed augmented dataset."

---

## SLIDE 16: Augmentation Effectiveness Comparison

### Speaker Notes:

> "This chart shows the relative effectiveness of different augmentation methods averaged across our benchmark tasks.
>
> The semantic methods cluster at the top — NaNa, MiGu, Conservative Substitute, and RSA all score above 75%. They work because they modify sequences in biologically plausible ways.
>
> BootGen and Back-Translation are in the middle tier. BootGen's quality-ranking mechanism helps, but it's more computationally expensive. Back-Translation's effectiveness depends on whether the model can benefit from nucleotide-level diversity.
>
> The random methods — Random Substitute, Random Shuffle — are at the bottom. They're useful as baselines and occasionally help on large datasets where the model can tolerate more noise, but they're not the methods you'd choose if you want consistent improvement.
>
> The takeaway: invest in domain-knowledge-driven augmentation. The biology matters."

---

## SLIDE 17: Conclusion

### Speaker Notes:

> "Four key takeaways:
>
> **One — Comprehensive framework**: We built EPA with 23 augmentation methods, 3 model types, and 8 datasets. This is the most thorough benchmark of protein augmentation to date.
>
> **Two — Semantic wins**: Methods that incorporate biochemical knowledge consistently outperform random approaches. NaNa's biophysical similarity scoring and MiGu's interaction preservation are particularly effective.
>
> **Three — Task-specific policies**: There is no universal best augmentation. The automated policy search is essential for finding the right combination for each task.
>
> **Four — Modular and extensible**: Adding a new augmentation method is as simple as writing a function with the signature `augment(sequence, intensity) -> sequence`. The framework handles everything else — policy search, training, evaluation."

---

## SLIDE 18: Future Work

### Speaker Notes:

> "Looking ahead, six directions:
>
> 1. **ESM-2 integration** — fine-tuning protein language models with augmentation. This could be transformative since ESM-2's pre-trained representations already capture protein structure.
>
> 2. **Cross-sequence mixing** for PreIS — implementing the full label-aware version where we mix segments from different proteins of the same class.
>
> 3. **Real homolog retrieval** for RSA — connecting to UniRef/Pfam with FAISS indexing so we augment with actual evolutionary relatives, not simulated ones.
>
> 4. **Advanced policy search** — replacing random search with reinforcement learning or Bayesian optimization to find better policies faster.
>
> 5. **Multi-task learning** — jointly training across multiple prediction tasks to see if augmentation benefits transfer.
>
> 6. **Structure-aware augmentation** — using 3D protein structure information to make even more biologically realistic augmentations."

---

## SLIDE 19: Q&A

> "Thank you. We're happy to take questions."

### Anticipated Questions & Answers:

**Q: How do you handle sequences of different lengths?**
> "All sequences are padded or truncated to a maximum length (default 512) during encoding. The augmentations work on the raw sequence before padding. Augmentations that change length (insert, delete, crop) produce sequences that then get padded/truncated to the fixed size."

**Q: Why not use pre-trained protein models like ESM from the start?**
> "ESM-2 integration is planned. We started with simpler models (LSTM, RF) to establish baselines and understand augmentation effects without the confound of a powerful pre-trained model. The augmentation techniques themselves are model-agnostic."

**Q: How do you know the augmented sequences are biologically valid?**
> "The semantic methods (NaNa, MiGu, RSA) are designed with biological constraints — they only make substitutions that are observed in natural protein evolution. The random methods don't guarantee biological validity, which is one reason they perform worse."

**Q: What's the computational overhead of augmentation?**
> "Token and sequence-level augmentations are nearly free — microseconds per sequence. Semantic methods like BootGen are slightly more expensive because they generate and score multiple candidates, but still under a millisecond per sequence. The main cost is in training, not augmentation."

**Q: How does this compare to augmentation in NLP or computer vision?**
> "Similar principles — synonym replacement in NLP is analogous to our conservative substitution, random cropping in vision is analogous to our sequence cropping. The difference is that protein augmentations can leverage deep domain knowledge (biochemistry, evolution, molecular interactions) that doesn't exist in general NLP/vision."
