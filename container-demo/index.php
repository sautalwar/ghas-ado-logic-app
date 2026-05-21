<?php

declare(strict_types=1);

require __DIR__ . '/vendor/autoload.php';

use GuzzleHttp\Client;
use Symfony\Component\HttpFoundation\Request;
use Twig\Environment;
use Twig\Loader\ArrayLoader;

$request = Request::createFromGlobals();
$client = new Client([
    'base_uri' => 'https://status.learfield.example',
    'timeout' => 2.0,
]);

$loader = new ArrayLoader([
    'dashboard' => <<<'TWIG'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Legacy PHP Container Demo</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; }
      code { background: #f3f3f3; padding: 0.2rem 0.4rem; }
    </style>
  </head>
  <body>
    <h1>Legacy PHP Container Demo</h1>
    <p>This app intentionally runs on <code>php:7.4-apache</code> with outdated Composer packages so Trivy can surface realistic findings.</p>
    <ul>
      <li><strong>Customer:</strong> Learfield</li>
      <li><strong>Mode:</strong> {{ mode }}</li>
      <li><strong>Health endpoint:</strong> {{ health_endpoint }}</li>
      <li><strong>Library example:</strong> {{ libraries }}</li>
    </ul>
  </body>
</html>
TWIG,
]);

$twig = new Environment($loader);
$appMode = (string) $request->query->get('mode', 'demo');

$libraries = implode(', ', [
    'guzzlehttp/guzzle 6.3.0',
    'symfony/http-foundation 2.7.0',
    'twig/twig 1.38.0',
]);

echo $twig->render('dashboard', [
    'mode' => $appMode,
    'health_endpoint' => (string) $client->getConfig('base_uri'),
    'libraries' => $libraries,
]);
