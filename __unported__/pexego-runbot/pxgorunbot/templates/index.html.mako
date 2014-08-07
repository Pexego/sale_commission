<!DOCTYPE html>
<html>
<head>
<title>Pexego Runbot</title>
<link rel="shortcut icon" href="/static/favicon.ico" />
<link rel="stylesheet" href="/static/css/runbot.css" type="text/css">
<script src="/static/js/jquery-1.7.1.min.js"></script>
<script src="/static/js/dropdown.js"></script>
<script src="/static/js/runbot.js"></script>
</head>
<body>
<div class="container">
    <div class="topbar">
      <ul class="nav">
        <li><a href="/"><img src="/static/img/logo.png" alt="" class="png"></a> </li>
        <li><a href="#">About</a> </li>
        <li><a href="/admin">Admin</a> </li>
      </ul>
      <div class="clear"></div>
    </div>
<div class="pane">
The Pexego Runbot is a simple yet useful Integration Server tailored for the
different Pexego projects available.
</div>
<div class="pane">
<h2>Projects</h2>
<ul>
% for project_name in r.projects_with_branches():
  <li><a href="/project/${project_name}">${project_name}</a></li>
% endfor
</ul>
</div>

</div>
</body>
