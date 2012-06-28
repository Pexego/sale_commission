<!DOCTYPE html>
<html>
<head>
  <title>Pexego Runbot - ${project_name}</title>
  <link rel="shortcut icon" href="/favicon.ico" />
  <link rel="stylesheet" href="css/runbot.css" type="text/css">
  <script src="js/jquery-1.7.1.min.js"></script>
  <script src="js/dropdown.js"></script>
  <script src="js/runbot.js"></script>
</head>
<body>

<%namespace name="defs" file="defs.html.mako"/>

  <div class="container">

    <div class="topbar">
      <ul class="nav">
        <li><a href="/"><img src="img/logo.png" alt="" class="png"></a> </li>
        <li class="dropdown" data-dropdown="dropdown">
          <a href="#" class="dropdown-toggle">Projects</a>
          <ul class="dropdown-menu">
% for tname in r.projects_with_branches():
    <li><a href="/${tname}.html">${tname}</a></li>
% endfor
          </ul>
        </li>
        <li><a href="#the-queue">Queue (${len(r.get_queue())})</a> </li>
        <li><a href="#">About</a> </li>
      </ul>
      <div class="clear"></div>
    </div>

    <h1>${project_name}</h1>

    <div class="pane">
      <h2>About</h2>
<p>The Pexego Runbot is a simple yet useful Integration Server tailored for the
different Pexego projects available. You can also
<a href="#code">grab a copy</a> and run it yourself.</p>

<p>Please note this is a static page, re-generated regularly. Any operation (e.g.
build) may not give an immediate feedback.</p>

<p>The Runbot maintains ${r.number} concurrent branches.</p>
    </div>

% if r.nginx_projects_development(project_name):
    <div class="pane">
      <!--<input class="searchbox" placeholder="Search branches...">-->
      <h2>Branches</h2>
      <table cellspacing="0">
% for i in r.nginx_projects_development(project_name):
    ${defs.short_row_(r,i)}
% endfor
      </table>
    </div>
% endif

    <div id="the-queue" class="pane">
<h2>Queue (${len(r.get_queue())} items)</h2>
<table>
% for i in r.get_queue():
    ${defs.simple_row(r,i)}
% endfor
</table>
    </div>

    <div class="pane">
      <h2>Runtime data</h2>
        <div class="stats">
        (The following data are global to the Runbot.)<br />
        Maximum ${r.number} concurrent branches.<br />
        ${r.current_job_id} processed jobs.<br />
        ${r.manual_build_count} manual build requests to go.<br />
        </div>
    </div>

  </div>

</body>
</html>
