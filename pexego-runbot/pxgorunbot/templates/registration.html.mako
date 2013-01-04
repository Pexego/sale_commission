<!DOCTYPE html>
<html>
<head>
<title>OpenERP Runbot</title>
<link rel="shortcut icon" href="/static/favicon.ico" />
<link rel="stylesheet" href="/static/style.css" type="text/css">
</head>
<body>
<div class="main-column">
<img src="/static/logo.png" /><br />
<a href="/">OpenERP Runbot</a><br /><br />

<h2 id="how">How to submit your team or branches</h2>
Before submitting anything, you have to make sure to follow some naming
convention. The Runbot is currently tracking four projects:
<ul>
<li><code>openobject-server</code></li>
<li><code>openobject-addons</code></li>
<li><code>openobject-client-web</code></li>
<li><code>openerp-web</code></li>
</ul>

For each project, Launchpad is hosting the code for a bunch of different
teams, each possibly having multiple branches. For instance the core
developers branches are under
<a href="https://launchpad.net/~openerp-dev">~openerp-dev</a>.

The official branches for those four projects are:
<ul>
<li><code>~openerp/openobject-server/6.0</code></li>
<li><code>~openerp/openobject-server/trunk</code></li>
<li><code>~openerp/openobject-addons/6.0</code></li>
<li><code>~openerp/openobject-addons/trunk</code></li>
<li><code>~openerp/openobject-client-web/6.0</code></li>
<li><code>~openerp/openerp-web/trunk</code></li>
</ul>

The convention is to prefix any branch with the main version of the official
branches. Let's say you are in the team <code>foo</code> and want to provide
a new feature <code>bar</code> in the server. You should name your branch as
follow:
<code>~foo/openobject-server/trunk-bar-feature</code>
The 3 important points in the naming convention is the name of the team (here
<code>foo</code>) the name of the project (here the server), and the prefix of
the branch name (here <code>trunk-</code>).

<h2 id="go">Submit your team or branches</h2>
<p>Please make sure to first read the section <a href="#how">above</a> before
submitting anything.</p>
<p>You can either submit a single branch, or a team. If you submit a team,
the Runbot will pick all your branches. In both cases, your team name will
appear in the list above, linking to a page with the build results.</p>
<br />
<form method="POST" action="/a/branch">
Submit a branch, e.g. <code>~foo/openobject-bar/trunk-baz</code><br />
<input id="branch-input" type="text" size="40" name="branch-input" value="" />
<input id="branch-submit" type="submit" value="Submit branch" />
</form>
<form method="POST" action="/a/team">
Submit a team, e.g. <code>foo</code><br />
<input id="team-input" type="text" size="40" name="team-input" value="" />
<input id="team-submit" type="submit" value="Submit team" />
</form>


<h2 id="go">Configure a build</h2>
If you don't respect the naming convention above, you can instead configure
manually a build by specifying which branches have to be used together.
<p>

</p>
<br />
<form method="POST" action="/a/configure-build">

<label for="team_name">Team name:</label><br />
<input id="team_name" type="text" size="40" name="team_name" value="" /><br />
<label for="name">Configuration name:</label><br />
<input id="name" type="text" size="40" name="name" value="" /><br />
<label for="version">Version (trunk or 6.0):</label><br />
<input id="version" type="text" size="40" name="version" value="trunk" /><br />
<label for="server_branch">Server:</label><br />
<input id="server_branch" type="text" size="40" name="server_branch" value="~openerp/openobject-server/trunk" /><br />
<label for="client_web_branch">Old web client:</label><br />
<input id="client_web_branch" type="text" size="40" name="client_web_branch" value="" /><br />
<label for="web_branch">Web client:</label><br />
<input id="web_branch" type="text" size="40" name="web_branch" value="~openerp/openerp-web/trunk" /><br />
<label for="addons_branch_0">Addons:</label><br />
<input id="addons_branch_0" type="text" size="40" name="addons_branch_0" value="~openerp/openobject-addons/trunk" /><br />
<label for="addons_branch_1">Addons:</label><br />
<input id="addons_branch_1" type="text" size="40" name="addons_branch_1" value="" /><br />
<label for="addons_branch_2">Addons:</label><br />
<input id="addons_branch_2" type="text" size="40" name="addons_branch_2" value="" /><br />
<label for="modules">Modules (comma-separated list of module names, no white-space):</label><br />
<input id="modules" type="text" size="40" name="modules" value="" /><br />
<input id="configuration-submit" type="submit" value="Submit configuration" />
</form>

</div>
</body>
