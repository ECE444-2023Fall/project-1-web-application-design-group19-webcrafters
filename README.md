<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
<h1 align="center">BETULA</h3>

  <p align="center">
    This project is a web application that allows Undergraduate University of Toronto students to post, register and browse events at the University.
  </p>
</div>

<!-- TABLE OF CONTENTS --> 

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details> 

<!-- ABOUT THE PROJECT -->
## About The Project

Betula is a web application designed to inform University of Toronto (UofT) undergraduate students about events occurring at the university. 

This is achieved by allowing hosts to post events that their group is hosting, and implementing an intuitive user interface to allow students to filter, search, select, save, and sign up for events they are interested in. 

The goals of this application would be to (1) help reduce the time for a student to find events they would enjoy, (2) enhance community engagement amongst UofT, and (3) help the undergraduate student body make the most of their social life at University.  

<p align="right">(<a href="#readme-top">back to top</a>)</p> 


### Built With

* [![Flask][Flask.com]][Flask-url]
* [![Docker][Docker.com]][Docker-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![SQL][SQL.com]][SQL-url]
* [![HTML][HTML.com]][HTML-url]
* [![CSS][CSS.com]][CSS-url]
* [![Python][Python.com]][Python-url]
* [![Figma][Figma.com]][Figma-url]
* [![Clapy][Clapy.com]][Clapy-url]


Additionally, our team uses KanbanFlow for project management. Our Kanban board is available [here](https://kanbanflow.com/board/ST3BL3S)!

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Currently our project has not been deployed. To use this project you must:

* Run ```$ git clone https://github.com/ECE444-2023Fall/project-1-web-application-design-group19-webcrafters ```
* Setup environment by running ```docker build -t python-docker .```
* Run the Docker container to view the webapp ```docker run -d -p 5000:5000 python-docker```
* Open [http://localhost:5000](http://localhost:5000)

To set up the database, you must:
* Send your IP address to our Software Lead at aniqa.tahseen@mail.utoronto.ca so that it can be added on the list of safe client IP addresses that can access the database
* Download the ODBC Driver:
  * WINDOWS: [https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)
  * MAC SILICON: Download this repo and add it to your workspace: [https://github.com/pypyodbc/pypyodbc](https://github.com/pypyodbc/pypyodbc)
* In the db_connection.py file, use the import pypyodbc line that is most relevant to your device
* Create a credential.py file with the username and password of the database - Reach out to aniqa.tahseen@mail.utoronto.ca or ava.jakob@mail.utoronto.ca for the credentials of the database
* Run the db_connection.py file only to connect to the database and get it up and running
* The database is being further refined and organized, the direct connection to the web app is still in progress, stay tuned for more instructions to come!

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Currently, we are not a stage in the development process where we are able to give a demonstration, but check back soon!!

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

To view our protocols on contributing, please refer to our [contribution instructions](https://github.com/ECE444-2023Fall/project-1-web-application-design-group19-webcrafters/blob/main/CONTRIBUTIONS.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

If you have any questions about Betula, feel free to contact our Project Manager available at sean.pourgoutzidis@mail.utoronto.ca

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Links & Images -->
[Flask.com]: https://img.shields.io/badge/Flask-563D7C?style=flask&logo=flask&logoColor=white&color=orange
[Flask-url]:https://flask.palletsprojects.com/en/3.0.x/
[Docker.com]: https://img.shields.io/badge/Docker-563D7C?logo=docker&logoColor=white&color=blue
[Docker-url]: https://www.docker.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[SQL.com]: https://img.shields.io/badge/SQL-563D7C?logo=mysql&logoColor=white&color=black
[SQL-url]: https://www.mysql.com
[HTML.com]: https://img.shields.io/badge/HTML-563D7C?logo=html5&logoColor=white&color=green
[HTML-url]: https://html.com
[CSS.com]: https://img.shields.io/badge/CSS-563D7C?logo=css3&logoColor=white&color=green
[CSS-url]: https://www.w3.org/Style/CSS/Overview.en.html
[Python.com]: https://img.shields.io/badge/Python-563D7C?logo=python&logoColor=white&color=yellow
[Python-url]: https://www.python.org
[Figma.com]: https://img.shields.io/badge/Figma-563D7C?logo=figma&logoColor=white&color=red
[Figma-url]: https://www.figma.com
[Clapy.com]: https://img.shields.io/badge/Clapy-563D7C?logo=clapy&logoColor=white&color=grey
[Clapy-url]: https://clapy.co
