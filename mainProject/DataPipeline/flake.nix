{
  description = "Scraper with rich-colored terminal output";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonEnv =
          pkgs.python3.withPackages (ps: with ps; [ pandas requests rich ]);
      in {
        devShell = pkgs.mkShell {
          buildInputs = [ pythonEnv ];
          shellHook = ''
            echo "🐍 [bold cyan]Python env ready with rich output[/bold cyan]"
          '';
        };
      });
}
