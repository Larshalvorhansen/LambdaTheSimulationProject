{ pkgs ? import <nixpkgs> { } }:

let
  python = pkgs.python312;
  pyPackages = python.pkgs;

in pkgs.mkShell {
  buildInputs = [
    python
    pyPackages.pandas
    pyPackages.matplotlib
    pyPackages.yfinance
    #    pyPackages.pandas-datareader
  ];

  # optional
  env.LD_LIBRARY_PATH =
    pkgs.lib.makeLibraryPath [ pkgs.zlib pkgs.openssl pkgs.stdenv.cc.cc ];
}
