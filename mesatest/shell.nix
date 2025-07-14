{ pkgs ? import (builtins.fetchTarball {
  url =
    "https://github.com/NixOS/nixpkgs/archive/f1a24397fc9fe10fd361aa84c480f3d5d9b3fc9e.tar.gz";
  sha256 = "1kn59zbq7hhp6mkm0ymsz98ig5lcjysyz3c1fgy0zv4gmz1xq7cg";
}) { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.mesa
    python311Packages.notebook
    python311Packages.matplotlib
    python311Packages.pandas
    python311Packages.ipykernel
  ];

  shellHook = ''
    echo "✅ Mesa dev shell ready. Run \`jupyter notebook\` or \`python\` to start."
  '';
}
