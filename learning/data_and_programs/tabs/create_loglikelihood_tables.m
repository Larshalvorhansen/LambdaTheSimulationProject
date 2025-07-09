%% Calculate Log-likelihood
clear;

% Load data
load ../data/data/1996.mat
load ../data/ea/1996.mat
data.gdp_deflator_quarterly=data.nominal_gdp_quarterly./data.real_gdp_quarterly; % calculate gdp deflator from levels
ea.gdp_deflator_quarterly=ea.nominal_gdp_quarterly./ea.real_gdp_quarterly; % calculate gdp deflator from levels

quarter_num=datenum(datetime('2019-09-30'));

Y0=[log(data.real_gdp_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.gdp_deflator_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.real_government_consumption_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.real_exports_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.real_imports_quarterly(data.quarters_num<=quarter_num)) ...
    log(ea.real_gdp_quarterly(ea.quarters_num<=quarter_num)) ...
    log(ea.gdp_deflator_quarterly(ea.quarters_num<=quarter_num)) ...
    cumsum((1+data.euribor(data.quarters_num<=quarter_num)).^(1/4)) ...
    ];

[logL_var, AIC_var, BIC_var, lagAIC_var, lagBIC_var]=loglikelihood(diff(Y0));

% generate LaTex code

% Set row labels (use empty string for no label):
input.tableRowLabels = {'VAR(1)','VAR(2)','VAR(3)'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=logL_var;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('logL_var.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

Y0=[log(data.real_gdp_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.gdp_deflator_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.real_household_consumption_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.real_fixed_capitalformation_quarterly(data.quarters_num<=quarter_num)) ...
    cumsum((1+data.euribor(data.quarters_num<=quarter_num)).^(1/4)) ...
    ];

logL_ar=zeros(3,size(Y0,2));
AIC_ar=zeros(3,size(Y0,2));
BIC_ar=zeros(3,size(Y0,2));
lagAIC_ar=zeros(3,1);
lagBIC_ar=zeros(3,1);
for l=1:size(Y0,2)
    [logL_ar(:,l), AIC_ar(:,l), BIC_ar(:,l), lagAIC_ar(l), lagBIC_ar(l)]=loglikelihood(diff(Y0(:,l)));
end

% generate LaTex code

% Set row labels (use empty string for no label):
input.tableRowLabels = {'AR(1)','AR(2)','AR(3)'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=logL_ar;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('logL_ar.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

X=[log(data.real_exports_quarterly) ...
    log(data.real_imports_quarterly) ...
    log(data.real_government_consumption_quarterly) ...
    ];

Y0=[log(data.real_gdp_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.gdp_deflator_quarterly(data.quarters_num<=quarter_num)) ...
    ];

[logL_varx, AIC_varx, BIC_varx, lagAIC_varx, lagBIC_varx]=loglikelihoodx(diff(Y0),diff(X));

% generate LaTex code

% Set row labels (use empty string for no label):
input.tableRowLabels = {'VARX(1)','VARX(2)','VARX(3)'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=logL_varx;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('logL_varx.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

X=[log(data.real_exports_quarterly) ...
    log(data.real_imports_quarterly) ...
    log(data.real_government_consumption_quarterly) ...
    ];

Y0=[log(data.real_gdp_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.gdp_deflator_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.real_household_consumption_quarterly(data.quarters_num<=quarter_num)) ...
    log(data.real_fixed_capitalformation_quarterly(data.quarters_num<=quarter_num)) ...
    cumsum(log(1+(1+data.euribor(data.quarters_num<=quarter_num)).^(1/4)-1)) ...
    ];

logL_arx=zeros(3,size(Y0,2)-1);
AIC_arx=zeros(3,size(Y0,2)-1);
BIC_arx=zeros(3,size(Y0,2)-1);
lagAIC_arx=zeros(3,1);
lagBIC_arx=zeros(3,1);
for l=1:size(Y0,2)-1
    [logL_arx(:,l), AIC_arx(:,l), BIC_arx(:,l), lagAIC_arx(l), lagBIC_arx(l)]=loglikelihoodx(diff(Y0(:,l)),diff(X));
end

% generate LaTex code

% Set row labels (use empty string for no label):
input.tableRowLabels = {'ARX(1)','ARX(2)','ARX(3)'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=logL_arx;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('logL_arx.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

Y0=log(data.nominal_nace10_gva_quarterly(data.quarters_num<=quarter_num,:));

logL_ar_nace10=zeros(3,size(Y0,2));
AIC_ar_nace10=zeros(3,size(Y0,2));
BIC_ar_nace10=zeros(3,size(Y0,2));
lagAIC_ar_nace10=zeros(3,1);
lagBIC_ar_nace10=zeros(3,1);
for l=1:size(Y0,2)
    [logL_ar_nace10(:,l), AIC_ar_nace10(:,l), BIC_ar_nace10(:,l), lagAIC_ar_nace10(l), lagBIC_ar_nace10(l)]=loglikelihood(diff(Y0(:,l)));
end

% generate LaTex code

% Set row labels (use empty string for no label):
input.tableRowLabels = {'AR(1)','AR(2)','AR(3)'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=logL_ar_nace10;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('logL_ar_nace10.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

Y0=log(data.nominal_nace10_gva_quarterly(data.quarters_num<=quarter_num,:));

[logL_var_nace10, AIC_var_nace10, BIC_var_nace10, lagAIC_var_nace10, lagBIC_var_nace10]=loglikelihood(diff(Y0));

% generate LaTex code

% Set row labels (use empty string for no label):
input.tableRowLabels = {'VAR(1)','VAR(2)','VAR(3)'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=logL_var_nace10;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('logL_var_nace10.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);
