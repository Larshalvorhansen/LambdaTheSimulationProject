% Clear workspace
clear;

year=2010;
quarter=4;

load(['../model/initial_conditions/',num2str(year),'Q',num2str(quarter),'.mat'],'D_I','L_I','omega','w_UB','sb_inact','sb_other','D_H','K_H','L_G','E_k','E_CB','D_RoW','N_s');

data=[D_I,L_I,omega,w_UB,sb_inact,sb_other,D_H,round(K_H,1),L_G,round(E_k,1),round(E_CB,1),D_RoW]';

% generate LaTex code

% Set column labels (use empty string for no label):
input.tableColLabels = {'Value'};

% Set row labels (use empty string for no label):
input.tableRowLabels = {'$D^{I}$','$L^{I}$','$\omega$','$w^{UB}$','$sb^{inact}(0)$','$sb^{other}(0)$','$D^{H}$','$K^{H}$','$L^{G}(0)$','$E_{k}(0)$','$E^{CB}(0)$','$D^{RoW}(0)$'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.4f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% LaTex table caption:
input.tableCaption = 'Initial conditions';

% LaTex table label:
input.tableLabel = 'initial_conditions';

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=cellstr(string(round(data,4)));
latex = latexTable(input);

% save LaTex code as file
fid=fopen('initial_conditions.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

load(['../model/parameters/',num2str(year),'Q',num2str(quarter),'.mat'],'S','G','H_act','H_inact','J','L', ...
    'I_s','alpha_s','beta_s','kappa_s','delta_s','w_s','tau_Y_s','tau_K_s','b_CF_g','b_CFH_g','b_HH_g','c_G_g','c_E_g','c_I_g','a_sg', ...
    'tau_INC','tau_FIRM','tau_VAT','tau_SIF','tau_SIW','tau_EXPORT','tau_CF','tau_G','r_G','mu','psi','psi_H','theta_DIV', ...
    'theta_UB','theta','zeta','zeta_LTV','zeta_b','pi_star', ...
    'alpha_G','beta_G','sigma_G','alpha_E','beta_E','alpha_I','beta_I','alpha_Y_EA','beta_Y_EA','alpha_pi_EA','beta_pi_EA','sigma_pi_EA','rho','r_star','xi_pi','xi_gamma');

data=[G,H_act,H_inact,J,L, ...
    tau_INC,tau_FIRM,tau_VAT,tau_SIF,tau_SIW,tau_EXPORT,tau_CF,tau_G,r_G,mu,psi,psi_H,theta_DIV, ...
    theta_UB,theta,zeta,zeta_LTV,zeta_b,pi_star, ...
    alpha_G,beta_G,sigma_G,alpha_E,beta_E,alpha_I,beta_I,alpha_Y_EA,beta_Y_EA,alpha_pi_EA,beta_pi_EA,sigma_pi_EA,rho,r_star,xi_pi,xi_gamma]';
data=round(data,4);

% generate LaTex code

% Set column labels (use empty string for no label):
input.tableColLabels = {'Value'};

% Set row labels (use empty string for no label):
input.tableRowLabels = {'$G/S$','$H^{act}$','$H^{inact}$','$J$','$L$', ...
    '$\tau^{INC}$','$\tau^{FIRM}$','$\tau^{VAT}$','$\tau^{SIF}$','$\tau^{SIW}$','$\tau^{EXPORT}$','$\tau^{CF}$','$\tau^{G}$','$r^{G}$','$\mu$','$\psi$','$\psi^{H}$','$\theta^{DIV}$', ...
    '$\theta^{UB}$','$\theta$','$\zeta$','$\zeta^{LTV}$','$\zeta^b$','$\pi^{*}$', ...
    '$\alpha^{G}$','$\beta^{G}$','$\sigma^{G}$','$\alpha^{E}$','$\beta^{E}$','$\alpha^{I}$','$\beta^{I}$','$\alpha^{Y^{EA}}$','$\beta^{Y^{EA}}$','$\alpha^{\pi^{EA}}$','$\beta^{\pi^{EA}}$','$\sigma^{\pi^{EA}}$','$\rho$','$r^{*}$','$\xi^{\pi}$','$\xi^{\gamma}$'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.4f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% LaTex table caption:
input.tableCaption = 'Scalar parameters';

% LaTex table label:
input.tableLabel = 'scalar_parameters';

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=cellstr(string(round(data,4)));
latex = latexTable(input);

% save LaTex code as file
fid=fopen('scalar_parameters.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

data=[I_s,N_s,alpha_s,beta_s,kappa_s,delta_s,w_s,tau_Y_s,tau_K_s,b_CF_g,b_CFH_g,b_HH_g,c_G_g,c_E_g,c_I_g];
data=round(data,4);

% generate LaTex code

% Set column labels (use empty string for no label):
input.tableColLabels = {'$I_s$','$N_{s}$','$\alpha_s$','$\beta_s$','$\kappa_s$','$\delta_s$','$w_s$','$\tau^{Y}_{s}$','$\tau^{K}_{s}$','$b^{CF}_g$','$b^{CFH}_{g}$','$b^{HH}_{g}$ ','$c^{G}_g$','$c^{E}_g$','$c^{I}_g$'};

% Set row labels (use empty string for no label):
input.tableRowLabels = {'A01','A02','A03','B','C10-12','C13-15','C16','C17','C18','C19','C20','C21','C22','C23','C24','C25','C26','C27','C28','C29','C30','C31\_32','C33','D','E36','E37-39','F','G45','G46','G47','H49','H50','H51','H52','H53','I','J58','J59\_60','J61','J62\_63','K64','K65','K66','L68A','M69\_70','M71','M72','M73','M74\_75','N77','N78','N79','N80-82','O','P','Q86','Q87\_88','R90-92','R93','S94','S95','S96'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.4f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% LaTex table caption:
input.tableCaption = 'Sector parameters';

% LaTex table label:
input.tableLabel = 'sector_parameters';

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

input.data=cellstr(string(round(data,4)));
latex = latexTable(input);

% save LaTex code as file
fid=fopen('sector_parameters.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);
