{
  description = "Scraper with rich-colored terminal output and wbdata";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        python = pkgs.python3Full; # includes pip
        pythonEnv = python.withPackages
          (ps: with ps; [ pandas requests rich pyperclip virtualenv ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv ];

          shellHook = ''
            echo "Python dev environment ready"

            if [ ! -d .venv ]; then
              echo "Creating virtualenv in .venv..."
              python -m venv .venv
            fi

            source .venv/bin/activate

            pip install --upgrade pip wheel

            pip install wbdata pandas requests rich pyperclip

            echo "All Python packages installed in .venv"
          '';
        };
      });
}
