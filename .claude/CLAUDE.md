# GeoThread — Project Recap + ASNAP Instructions  
Sources: :contentReference[oaicite:0]{index=0} , :contentReference[oaicite:1]{index=1}  

---

## 1. Overview  
GeoThread is a Reddit-inspired social platform.  
It focuses on hyper-local interactions.  
It connects users based on proximity.  
It combines social networking and geolocation.  
It introduces a dynamic personalized feed.  
It aims to reduce digital isolation.  
It emphasizes nearby community engagement.  

---

## 2. Vision & Positioning  
“The internet divides us. Let’s bring together the people next to you.”  
Local-first social networking approach.  
Focus on relevance over global noise.  
Encourages meaningful nearby interactions.  

---

## 3. Core Concept  
Reddit-inspired structure.  
Subreddits and communities.  
Posts and interactions.  
Upvotes and downvotes.  
Nested comment threads.  
Single homepage feed.  
Location-aware ranking system.  

---

## 4. Feed System  
Dynamic and personalized feed.  
Based on preferences and filters.  
Includes geographic radius filtering.  
Supports multiple sorting modes:  
- Trending  
- Closest  
- New  

---

## 5. System Architecture  
Frontend built with React.  
Backend built with Python API.  
Database uses PostgreSQL.  
Service-oriented architecture.  

Backend responsibilities:  
- Ranking  
- Filtering  
- Distance computation  
- Feed generation  

Feed pipeline:  
Retrieve → Filter → Score → Sort → Feed  

---

## 6. Data Model  
Graph-based model.  
Entities:  
- Users  
- Posts  
- Comments  
- Subreddits  
- Interactions  

Relationships are interconnected.  
Supports complex graph queries.  

---

## 7. Core Features  
Create posts.  
Join communities.  
Vote on content.  
Comment on posts.  
Browse personalized feed.  

---

## 8. Location Features  
Optional location activation.  
Manual post tagging.  
Geographic radius filtering.  
Distance-aware ranking.  

---

## 9. Nested Comments System  
Hierarchical structure.  
Supports deep reply chains.  
Uses N-ary trees.  

Algorithm:  
Depth-First Search (DFS).  
Ensures correct rendering order.  

Storage:  
Modified Preorder Tree Traversal.  

---

## 10. Feed Ranking System  
Challenge: relevance vs freshness.  

Data structure:  
Max-Heap / Priority Queue.  

Algorithm:  
Time-decay scoring.  
Logarithmic scaling of upvotes.  
Time penalty applied.  

Multi-factor ranking:  
- Engagement  
- Time  
- Location  

---

## 11. Strengths  
Rich algorithmic diversity.  
Highly personalized feed.  
Clear data hierarchy.  
Good for scaling strategies.  

---

## 12. Weaknesses  
High computational cost.  
Complex database schema.  
Cold start for location.  

---

## 13. Opportunities  
Hyper-local niche.  
Use of geospatial DBs (PostGIS).  
Targeted local content and ads.  

---

## 14. Threats  
Privacy concerns.  
Strong competitors.  
Scalability challenges.  

---

## 15. Development Environment  
Dockerized architecture.  
Multi-container setup.  
React frontend.  
Python backend.  
PostgreSQL database.  

Optional tools:  
Redis.  
WebSockets.  
S3 storage.  
Nginx proxy.  

---

## 16. Project Planning  
Phases:  
- Modeling  
- Design  
- Algorithms  
- Implementation  
- Testing  

Modeling: define graph and problem.  
Design: structures and complexity.  
Algorithms: ranking, filtering, distance.  
Implementation: integration and optimization.  

---

# 🔥 ASNAP PROJECT INSTRUCTIONS (Course Requirements)

## 17. Project Objective  
Design the algorithmic intelligence of a social network.  
Build ASNAP (Advanced Social Network Algorithms Platform).  
Focus on backend intelligence.  
Apply graph theory and algorithms. :contentReference[oaicite:2]{index=2}  

---

## 18. Core Mission  
Create a backend engine.  
Power features such as:  
- Recommendations  
- Community detection  
- Trend analysis  
- Network operations  

Solve real-world scalability problems.  

---

## 19. Inspiration Platforms  
Choose or model after:  
- LinkedIn (career graphs)  
- YouTube (recommendation chains)  
- Twitter/X (information spread)  
- Facebook (social graphs)  
- Instagram (engagement networks)  
- TikTok (viral content)  
- Reddit (discussion trees)  
- Discord (interaction graphs)  
- Snapchat (proximity networks)  
- Pinterest (interest graphs)  

GeoThread aligns with Reddit + Snapchat hybrid.  

---

## 20. Team Requirements  
Teams of 3 students.  
Same TP group.  

---

## 21. Core Deliverables  

### 21.1 Platform Definition  
Define the platform purpose.  
Identify main use-case.  
Explain system behavior.  

### 21.2 Algorithm Implementation  
Implement key algorithms.  
Must be course-related.  
Examples:  
- Graph traversal  
- Recommendation systems  
- Ranking algorithms  
- Community detection  

---

## 22. Integration Requirement  
Integrate algorithms into one system.  
Create a cohesive backend engine.  
Ensure components interact correctly.  

---

## 23. Testing & Evaluation  
Test with multiple datasets.  
Analyze performance.  
Measure efficiency.  

---

## 24. Demonstration  
Provide working demo.  
Simple UI or API is enough.  
Show algorithm intelligence.  

---

## 25. Documentation  
Explain design decisions.  
Describe architecture.  
Detail algorithms.  
Include results and analysis.  

---

## 26. Technical Constraints  

### 26.1 Version Control  
Git is mandatory.  

### 26.2 Algorithm Ownership  
All core algorithms must be self-implemented.  

### 26.3 Graph-Based Model  
System must be graph-centered.  

### 26.4 Progressive Development  
Built incrementally during TP sessions.  

---

## 27. How GeoThread Fits ASNAP  

GeoThread fully aligns with ASNAP requirements:  

Graph model → users, posts, comments.  
DFS → comment tree traversal.  
Heap → feed ranking.  
Multi-factor ranking → recommendation system.  
Location → additional graph di/mension.  

---

## 28. Final Positioning  

GeoThread is not just a social app.  
It is an ASNAP-compliant backend engine.  
It demonstrates:  
- Graph algorithms  
- Real-world system design  
- Scalable architecture  
- Intelligent feed generation  

It directly answers the project objective.  

---