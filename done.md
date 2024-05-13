relations done
- [x] many to many relationships
    - [x] user.completed_mazes -> maze.solvers
    - [x] user.badges -> badges.users 

    - [x] maze.tags -> tags.mazes 
    - [x] maze.solvers -> user.completed_maze 
    - [x] user.enrolled_mazes -> maze.enrolled_users

- [x] one to many
    - [x] user.created_mazes -> maze.owner
    - [x] maze.pages -> page.maze
    - [x] page.questions -> question.page