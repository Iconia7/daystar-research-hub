-- ============================================================================
-- DAYSTAR DATABASE SEEDING SCRIPT
-- ============================================================================
--
-- This script provides sample data for development and testing.
-- Runs AFTER 01-init.sql extensions are created.
--
-- Sample data includes:
-- - 5 researchers across multiple departments
-- - 10 publications with SDG tags
-- - Collaborations between researchers
-- - Authorships linking researchers to publications
--
-- ============================================================================

-- Disable constraints during seeding
SET session_replication_role = 'replica';

-- ============================================================================
-- SEED USERS (Django auth_user table)
-- ============================================================================

INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
VALUES
  (1, 'pbkdf2_sha256$260000$abcdefghijklmnop$1234567890abcdefghijklmnop=', NOW(), true, 'admin', 'Admin', 'User', 'admin@research.edu', true, true, NOW()),
  (2, 'pbkdf2_sha256$260000$abcdefghijklmnop$1234567890abcdefghijklmnop=', NOW(), false, 'alice_smith', 'Alice', 'Smith', 'alice@research.edu', false, true, NOW()),
  (3, 'pbkdf2_sha256$260000$abcdefghijklmnop$1234567890abcdefghijklmnop=', NOW(), false, 'bob_johnson', 'Bob', 'Johnson', 'bob@research.edu', false, true, NOW()),
  (4, 'pbkdf2_sha256$260000$abcdefghijklmnop$1234567890abcdefghijklmnop=', NOW(), false, 'carol_williams', 'Carol', 'Williams', 'carol@research.edu', false, true, NOW()),
  (5, 'pbkdf2_sha256$260000$abcdefghijklmnop$1234567890abcdefghijklmnop=', NOW(), false, 'david_brown', 'David', 'Brown', 'david@research.edu', false, true, NOW()),
  (6, 'pbkdf2_sha256$260000$abcdefghijklmnop$1234567890abcdefghijklmnop=', NOW(), false, 'emma_davis', 'Emma', 'Davis', 'emma@research.edu', false, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SEED RESEARCHERS
-- ============================================================================

INSERT INTO research_graph_researcher (id, user_id, department, research_interests, google_scholar_id, created_at, updated_at)
VALUES
  (1, 2, 'Computer Science', ARRAY['Machine Learning', 'AI', 'Deep Learning', 'Neural Networks'], 'alice_scholar_id', NOW(), NOW()),
  (2, 3, 'Computer Science', ARRAY['Data Science', 'Big Data', 'Analytics', 'Python'], 'bob_scholar_id', NOW(), NOW()),
  (3, 4, 'Environmental Science', ARRAY['Climate Change', 'Sustainability', 'Ecology', 'Carbon Footprint'], 'carol_scholar_id', NOW(), NOW()),
  (4, 5, 'Computer Science', ARRAY['Natural Language Processing', 'NLP', 'Text Analysis', 'AI'], 'david_scholar_id', NOW(), NOW()),
  (5, 6, 'Environmental Science', ARRAY['Renewable Energy', 'Solar Power', 'Wind Energy', 'Clean Technology'], 'emma_scholar_id', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SEED PUBLICATIONS
-- ============================================================================

INSERT INTO research_graph_publication (id, title, abstract, publication_date, doi, sdg_tags, sdg_auto_generated, created_at, updated_at)
VALUES
  (1, 
    'Deep Learning Applications in Climate Prediction',
    'This paper presents a novel deep learning approach for predicting climate patterns using historical data. Our model achieves 87% accuracy in forecasting temperature changes.',
    '2023-06-15',
    '10.1234/example.2023.001',
    ARRAY['SDG_13', 'SDG_7'],
    true,
    NOW(), NOW()),
  
  (2,
    'Scalable Data Processing for Large-Scale Research',
    'We propose a distributed data processing framework for handling petabyte-scale research datasets. The framework reduces processing time by 60% compared to traditional approaches.',
    '2023-09-22',
    '10.1234/example.2023.002',
    ARRAY['SDG_9', 'SDG_12'],
    true,
    NOW(), NOW()),
  
  (3,
    'Machine Learning for Sustainable Development Goals',
    'This study explores how machine learning algorithms can be applied to identify and measure progress toward UN Sustainable Development Goals.',
    '2023-12-01',
    '10.1234/example.2023.003',
    ARRAY['SDG_13', 'SDG_7', 'SDG_9'],
    true,
    NOW(), NOW()),
  
  (4,
    'Natural Language Processing for Environmental Policy Analysis',
    'We develop NLP models to analyze environmental policy documents and extract key sustainability indicators across different countries.',
    '2024-01-10',
    '10.1234/example.2024.001',
    ARRAY['SDG_13', 'SDG_16'],
    true,
    NOW(), NOW()),
  
  (5,
    'Renewable Energy Optimization Using AI',
    'This paper presents AI-based optimization techniques for maximizing renewable energy generation and grid stability.',
    '2024-02-15',
    '10.1234/example.2024.002',
    ARRAY['SDG_7', 'SDG_9'],
    true,
    NOW(), NOW()),
  
  (6,
    'Collaborative Research Networks in Climate Science',
    'A comprehensive analysis of collaboration patterns in climate science research and their impact on research quality and innovation.',
    '2023-08-20',
    '10.1234/example.2023.004',
    ARRAY['SDG_13', 'SDG_17'],
    true,
    NOW(), NOW()),
  
  (7,
    'Data Privacy in Large-Scale Research Collaborations',
    'We propose novel privacy-preserving techniques for sharing sensitive research data across institutional boundaries.',
    '2023-11-05',
    '10.1234/example.2023.005',
    ARRAY['SDG_16', 'SDG_17'],
    true,
    NOW(), NOW()),
  
  (8,
    'Carbon Footprint Analysis of ICT Infrastructure',
    'This study quantifies the environmental impact of information and communication technology infrastructure.',
    '2023-10-12',
    '10.1234/example.2023.006',
    ARRAY['SDG_12', 'SDG_13'],
    true,
    NOW(), NOW()),
  
  (9,
    'Interdisciplinary Approaches to Climate Action',
    'An exploration of how different academic disciplines contribute to climate action and environmental sustainability.',
    '2024-01-25',
    '10.1234/example.2024.003',
    ARRAY['SDG_13', 'SDG_17'],
    true,
    NOW(), NOW()),
  
  (10,
    'Machine Learning in Medical Diagnostics',
    'Recent advances in machine learning for improving diagnostic accuracy in clinical settings.',
    '2024-02-01',
    '10.1234/example.2024.004',
    ARRAY['SDG_3', 'SDG_9'],
    true,
    NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SEED AUTHORSHIPS (Researcher-Publication links)
-- ============================================================================

INSERT INTO research_graph_authorship (id, researcher_id, publication_id, order, created_at)
VALUES
  -- Publication 1: Alice (lead), Bob
  (1, 1, 1, 1, NOW()),
  (2, 2, 1, 2, NOW()),
  
  -- Publication 2: Bob (lead), Alice
  (3, 2, 2, 1, NOW()),
  (4, 1, 2, 2, NOW()),
  
  -- Publication 3: Alice, David, Carol
  (5, 1, 3, 1, NOW()),
  (6, 4, 3, 2, NOW()),
  (7, 3, 3, 3, NOW()),
  
  -- Publication 4: David (lead)
  (8, 4, 4, 1, NOW()),
  
  -- Publication 5: Emma (lead)
  (9, 5, 5, 1, NOW()),
  
  -- Publication 6: All researchers
  (10, 1, 6, 1, NOW()),
  (11, 2, 6, 2, NOW()),
  (12, 3, 6, 3, NOW()),
  (13, 4, 6, 4, NOW()),
  (14, 5, 6, 5, NOW()),
  
  -- Publication 7: Alice, Carol
  (15, 1, 7, 1, NOW()),
  (16, 3, 7, 2, NOW()),
  
  -- Publication 8: Carol, Emma
  (17, 3, 8, 1, NOW()),
  (18, 5, 8, 2, NOW()),
  
  -- Publication 9: All except Bob
  (19, 1, 9, 1, NOW()),
  (20, 3, 9, 2, NOW()),
  (21, 4, 9, 3, NOW()),
  (22, 5, 9, 4, NOW()),
  
  -- Publication 10: Bob, David
  (23, 2, 10, 1, NOW()),
  (24, 4, 10, 2, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SEED COLLABORATIONS (Researcher-Researcher links)
-- ============================================================================

INSERT INTO research_graph_collaboration (id, researcher_1_id, researcher_2_id, strength, last_collaborated, created_at)
VALUES
  -- Alice - Bob (strong CS collaboration)
  (1, 1, 2, 5, '2024-02-01', NOW()),
  
  -- Alice - David (AI/NLP research)
  (2, 1, 4, 4, '2024-01-15', NOW()),
  
  -- Alice - Carol (interdisciplinary)
  (3, 1, 3, 3, '2023-12-01', NOW()),
  
  -- Alice - Emma (climate tech)
  (4, 1, 5, 2, '2023-10-01', NOW()),
  
  -- Bob - David (data science)
  (5, 2, 4, 3, '2024-01-20', NOW()),
  
  -- Bob - Emma (emerging interest)
  (6, 2, 5, 1, '2023-08-01', NOW()),
  
  -- Carol - Emma (environmental focus)
  (7, 3, 5, 4, '2024-01-01', NOW()),
  
  -- David - Carol (sustainability)
  (8, 4, 3, 2, '2023-11-01', NOW())
ON CONFLICT (id) DO NOTHING;

-- Re-enable constraints
SET session_replication_role = 'default';

-- ============================================================================
-- DISPLAY SUMMARY
-- ============================================================================

SELECT 'Database seeding completed successfully!' as status;
SELECT COUNT(*) as researcher_count FROM research_graph_researcher;
SELECT COUNT(*) as publication_count FROM research_graph_publication;
SELECT COUNT(*) as authorship_count FROM research_graph_authorship;
SELECT COUNT(*) as collaboration_count FROM research_graph_collaboration;
