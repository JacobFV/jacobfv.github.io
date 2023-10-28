---
layout: post
title: P versus NP
date: 2023-08-14
description: An incomplete endevour to solve the Problem
hidden: true
categories: [math, theory]
tags:
---

Bridging both the practical and the theoretical, permeating nearly every domain, a longstanding question of computer science stands the Problem. Succintly,

$$
\begin{equation}
\text{Does P} = \text{NP?}
\end{equation}
$$

where:
- $
\text{P} = \{ p \in \mathcal{D} \mid \exists a \in \mathcal{A} : \text{a solves p in polynomial time}\}
$
- $
\text{NP} = \{ p \in \mathcal{D} \mid \exists a \in \mathcal{A} : \text{a verifies a solution to p in polynomial time}\}
$
- $\mathcal{D}$ is the set of all decision problems
- $\mathcal{A}$ is the set of all algorithms

To solve it is not a mere exercise in curiosity, but -- as we will see -- transcendence beyond the very nature of provable nature of computation itself. Yet such is our aim.

Consider *this* proof $p_{this}$ and its implications: Either
$$
\begin{equation}
p_{this} \rightarrow \text{P}=\text{NP} \tag{2}
\end{equation}
$$

$$
\begin{equation}
p_{this} \rightarrow \text{P}\neq\text{NP} \tag{3}
\end{equation}
$$

or

$$
\begin{equation}
p_{this} \rightarrow \text{P}=\text{NP} \land \text{P}\neq\text{NP} \tag{4}
\end{equation}
$$

For convenience, let us define constants for $p_{this}$'s self-referential implication $p_{\text{P}=\text{NP}}$ \eqref{eq:2}, disproof $p_{\text{P}\neq \text{NP}}$ \eqref{eq:3}, and impossibility $p_{\text{P}=\text{NP} \wedge \text{P}\ne\text{NP}}$ \eqref{eq:4}. The latter is necesary to distinguish between provable and unprovable impossibilities, as we will see.

Now how shall we proceed? Abstractly, proof is the goal-directed application of implication rules $\mathcal{R}$ to a set of axioms $\mathcal{S}_0$.

1. Start by establishing our known axioms $\mathcal{S}_0 = \{ s_1, s_2, s_3, \dots, s_n \}$,
2. Select an implication to apply $r_i \in \mathcal{R}$ to apply to $\mathcal{S}_0$,
3. Repeat, building a sequence of larger and larger axiom sets $\mathcal{S}_i = \mathcal{S}_{i-1} \cup \mathcal{r}(\mathcal{S_{i-1}})$,
4. Stop when $\mathcal{S}_i$ contains a statement $s_n$ that we are trying to prove.

Note the distinction between the proof *process* and the final proof itself. The latter lends itself a direct step-by-step verification, whereas the former demands a graph search. Proof verification surely takes less time... Or does it?

The Cook-Levin theorom shows that if $\text{P}=\text{NP}$, then there must exist a polynomial running time complexity algorithm that solves graph search, an NP-Complete problem. As we have just seen, proof solving is a form of graph search. Thus, if $\text{P}=\text{NP}$, then the proof search algorithm most definitely runs in a countable number of steps with respect to the proof length, but depending on the value of $p_{this}$ the proof search algorithm may not.

If $\text{P}=\text{NP}$, then the proof search algorithm most definitely runs in a countable number of steps with respect to the proof length, but depending on the value of $p_{this}$ the proof search algorithm may not.


How how neigher of these solutions offer a solution.

If I show both are true, then I've just shown that P<>NP is orthogonal to the current axiomatic system

Discuss how it possible to continue building larger and larger axiomatic system by adding orthogonal dimensions to the axiom space

And discuss how there are level requirements for understanding a more complex / powerful paradigm: first by understanding the cumulative sum of simpler predessor paradigms to it.

Maybe paradigms are like clusters in a graph that typically must be arrived at via highway

Simulate all possible aiomatic spaces and show what they look like in the limit of all random choices







<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>



most definitely runs in a countable number of steps with respect to the proof length, but depending on the value of $p_{this}$ the proof search algorithm may not.

Let $M_p$ be a proof solving Turing machine and $M_v$ be its verifier. $M_p$ works by nondeterministically applying all possible implication rules to an initial set of axioms $\mathcal{S}$ ($p_n = \delta(p_{n-1})$, $p_0=\mathcal{S}_0$) until it reaches a set of statements containing a subgraph matching the statement it is trying to prove. On the other hand, $M_v$ receives a given sequence of implication rules all possible implication rules to a proof $p$ and checking that each step is valid.

As the proof is merely an implication chain, $M_v$ clearly halts within a polynomial order of steps compared to the proof length. On the other hand, if $\text{P}\ne\text{NP}$, then it may simply be impossible to linearize the nondeterministic branches of $M_p$'s execution into a sequence of polynomial length with respect to the proof length. Thus, if $\text{P}\ne\text{NP}$, $M_p$ is not guaranteed to halt within a countable number of steps. Furthur, if both $\text{P}=\text{NP}$ and $\text{P}\ne\text{NP}$, then $M_p$ *is* guaranteed to never halt, and vice versa. We will return to this later.

But first, let us consider our first two options: either $\text{P}=\text{NP}$ or $\text{P}\ne\text{NP}$. In the former case, $M_p$ must halt in polynomial time, and thus both $p_{this}$ can be proved and its proof can be checked. In the latter case, $M_p$ may or may not prove a statement within a countable number of implication steps, and thus there may exist checkable-proofs that cannot be found.

By "may or may not", we refer to the graph traversal and backtracking that $M_p$ must make. TODO: explain the branching part. Show how this is a graph search problem. Explain how the proof itself is a path through this graph. Explain how the proof checking is a step-by-step walk through the proof itself, verifying each step's validity. Show how P=NP means the graph can be solved easily, and P!=NP means the graph cannot be solved easily. WAIT NO: because P=NP may be an average case problem, so even if the worst case for graph search is exponential P v NP may not be

Now what can be said about unprovable proofs? Godel put it best: "This sentence is unprovable." If it is provable, then it is unprovable. If it is unprovable, then it is provable. Thus, it is both provable and unprovable. This is a contradiction, and thus it is impossible. Thus, there are no statements with unprovable proofs. And yet, if $\text{P}\ne\text{NP}$, we end up in a situation where there exist statements whose proof the verifier $M_v \in \text{P}$ may verify within a countable steps but that the solver $M_p \in \text{NP}$ may not halt discover within a countable number of steps. If $p_{\text{P}\ne\text{NP}}$'s proof search was exponential wrt input (worse case), then $\text{P}\ne\text{NP}$ implicates the existance of unprovable statements, which is impossible. Thus, $p_{this}$ disproves $p_{\text{P}\ne\text{NP}}$.

No; rather than p_this disproving anything, consider the two cases
- P!=NP and p_this requires exponential dtime
- P!=NP and p_this only requires Ptime <- this option is still open

However Godel had more to say about unprovable proofs. His second incompleteness theorom states that no complete axiomatic system can prove its own consistency. $p_{this}$'s self-referential proof (right here) is most certainly a statement about its completeness. Therefore $p_{this}$ cannot be consistent. So we must also rule out both $p_{\text{P}=\text{NP}}$ and $p_{\text{P}\ne\text{NP}}$ as impossible.

Finally, consider $p_{\text{P}=\text{NP} \wedge \text{P}\ne\text{NP}}$: As discussed earlier, $p_{this}$'s existance necesitates that $M_p$ to halt. A halting $M_p$ requires $P=NP$. $p_{\text{P}=\text{NP} \wedge \text{P}\ne\text{NP}}$ implies $M_p$ does not exist. And yet here you are reading its proof right now. Thus, your existance demands $M_p$ to halt, or else $p_{this}$ is unprovable. Note, ruling out $p_{\text{P}=\text{NP} \wedge \text{P}\ne\text{NP}}$ as impossible does not remove the possiblility that $p_{this}$ is itself inconsistent, which by Godel's 1st incompleteness theorom is the default for a self-referrential statement as $p_{this}$. However, if we end up here, we might try proving equivalence between $p_{this}$ and Godel's statement, which would implicate an impossibility proof of $p_{this}$.

Having exhaust all three cases, we conclude that $p_{this}$ is impossible. Thus, not only do we not have a proof for the Problem, we will never have a proof for the Problem. Thus, the Problem does not exist.

This is good news for computer scientists because it means they will have a job for the rest of their lives. This is bad news for computer scientists because it means they will have a job for the rest of their lives. That problem is not halting either.





<br>
<br>



1. make a countable sequence of related implications $\mathcal{P} = \{ \bigwedge_{s_i \in \mathcal{S}} s_i \rightarrow p_1$, $(\bigwedge_{s_i \in \mathcal{S}} s_i) \land p_1 \rightarrow p_2$, $(\bigwedge_{s_i \in \mathcal{S}} s_i) \land p_1 \land p_2 \rightarrow p_3, \dots, (\bigwedge_{s_i \in \mathcal{S}} s_i) \land (\bigwedge_{p_i \in \{p_1 \dots p_{n-1}\}} p_i) \rightarrow p_n \}$ progressively implying their successors, and
2. conclude when this implication chain reaches $p_n \rightarrow p_{\text{P}=\text{NP}}$, $p_n \rightarrow p_{\text{P}\neq \text{NP}}$, or $p_n \rightarrow p_{\text{P}=\text{NP} \wedge \text{P}\ne\text{NP}}$.
