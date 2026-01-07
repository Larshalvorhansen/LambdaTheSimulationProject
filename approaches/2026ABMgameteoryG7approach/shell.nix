{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages
      (p: with p; [ numpy pandas scipy seaborn matplotlib ]))
  ];
}
