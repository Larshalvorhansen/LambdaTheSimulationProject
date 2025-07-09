%% Monte Carlo simulation of autoregressive model with exogenous variables

clear;
year_=2010;
number_years=10;
number_quarters=4*number_years;
quarters_num=datenum(year_,4:3:(number_years+1)*12+1,0);
horizon=12;
number_seeds=500;

% Load data
load('../data/data/1996.mat');

for i=1:number_quarters-1
    
    horizon=min(horizon,28-i+12);
    
    quarter_num=quarters_num(i);
    year_num=datenum(datetime(year(datetime(datestr(quarter_num)))+1,1,0));
    
    forecast_quarter_num=datenum(datetime(year(datetime(datestr(quarter_num))),month(datetime(datestr(quarter_num)))+(3*horizon)+1,0));
    q=quarter(datetime(datestr(quarters_num(i))));
    
    X=[diff(log(data.real_exports_quarterly)) ...
        diff(log(data.real_imports_quarterly)) ...
        diff(log(data.real_government_consumption_quarterly)) ...
    ];
    X(:,1:3)=cumsum(X(:,1:3));
    
    Y0=[diff(log(data.real_gdp_quarterly(data.quarters_num<=quarter_num))) ...
        diff(log(data.nominal_gdp_quarterly(data.quarters_num<=quarter_num)./data.real_gdp_quarterly(data.quarters_num<=quarter_num))) ...
        diff(log(data.real_household_consumption_quarterly(data.quarters_num<=quarter_num))) ...
        diff(log(data.real_fixed_capitalformation_quarterly(data.quarters_num<=quarter_num)))
     ];
    Y0(:,[1 3 4])=cumsum(Y0(:,[1 3 4]));
    
    V=zeros(horizon,4,number_seeds);
    parfor j=1:4
        V(:,j,:)=simulate_arx(Y0(:,j),horizon,number_seeds,X);
    end
    V=[V;NaN(12-horizon,4,number_seeds)];
    
    real_gdp_quarterly=data.real_gdp_quarterly(data.quarters_num==quarter_num)*exp(squeeze(V(:,1,:))-Y0(end,1));
    arx.real_gdp_quarterly=[repmat(data.real_gdp_quarterly(data.quarters_num==quarter_num),1,number_seeds);real_gdp_quarterly];
    arx.real_gdp=[repmat(data.real_gdp(data.years_num==year_num),1,number_seeds);toannual(real_gdp_quarterly(5-q:end-mod(q,4),:)')'];
    arx.real_gdp_growth=diff(log([repmat(data.real_gdp(data.years_num==year_num),1,number_seeds);toannual(real_gdp_quarterly(5-q:end-mod(q,4),:)')']));
    % calculate discrete compounding rate
    arx.real_gdp_growth=exp(arx.real_gdp_growth)-1;
    arx.real_gdp_growth=[repmat(data.real_gdp_growth(data.years_num==year_num),1,number_seeds);arx.real_gdp_growth];
    
    arx.real_gdp_growth_quarterly=diff(log([repmat(data.real_gdp_quarterly(data.quarters_num==quarter_num),1,number_seeds);real_gdp_quarterly]));
    % calculate discrete compounding rate
    arx.real_gdp_growth_quarterly=exp(arx.real_gdp_growth_quarterly)-1;
    arx.real_gdp_growth_quarterly=[repmat(data.real_gdp_growth_quarterly(data.quarters_num==quarter_num),1,number_seeds);arx.real_gdp_growth_quarterly];
    
    gdp_deflator_quarterly=data.gdp_deflator_quarterly(data.quarters_num==quarter_num)*exp(cumsum(squeeze(V(:,2,:))));
    arx.gdp_deflator_quarterly=[repmat(data.gdp_deflator_quarterly(data.quarters_num==quarter_num),1,number_seeds);gdp_deflator_quarterly];
    arx.gdp_deflator=[repmat(data.gdp_deflator(data.years_num==year_num),1,number_seeds);toannual_mean(gdp_deflator_quarterly(5-q:end-mod(q,4),:)')'];
    arx.gdp_deflator_growth=diff(log([repmat(data.gdp_deflator(data.years_num==year_num),1,number_seeds);toannual_mean(gdp_deflator_quarterly(5-q:end-mod(q,4),:)')']));
    % calculate discrete compounding rate
    arx.gdp_deflator_growth=exp(arx.gdp_deflator_growth)-1;
    arx.gdp_deflator_growth=[repmat(data.gdp_deflator_growth(data.years_num==year_num),1,number_seeds);arx.gdp_deflator_growth];
    
    arx.gdp_deflator_growth_quarterly=diff(log([repmat(data.gdp_deflator_quarterly(data.quarters_num==quarter_num),1,number_seeds);gdp_deflator_quarterly]));
    % calculate discrete compounding rate
    arx.gdp_deflator_growth_quarterly=exp(arx.gdp_deflator_growth_quarterly)-1;
    arx.gdp_deflator_growth_quarterly=[repmat(data.gdp_deflator_growth_quarterly(data.quarters_num==quarter_num),1,number_seeds);arx.gdp_deflator_growth_quarterly];
    
    real_household_consumption_quarterly=data.real_household_consumption_quarterly(data.quarters_num==quarter_num)*exp(squeeze(V(:,3,:))-Y0(end,3));
    arx.real_household_consumption_quarterly=[repmat(data.real_household_consumption_quarterly(data.quarters_num==quarter_num),1,number_seeds);real_household_consumption_quarterly];
    arx.real_household_consumption=[repmat(data.real_household_consumption(data.years_num==year_num),1,number_seeds);toannual(real_household_consumption_quarterly(5-q:end-mod(q,4),:)')'];
    arx.real_household_consumption_growth=diff(log([repmat(data.real_household_consumption(data.years_num==year_num),1,number_seeds);toannual(real_household_consumption_quarterly(5-q:end-mod(q,4),:)')']));
    % calculate discrete compounding rate
    arx.real_household_consumption_growth=exp(arx.real_household_consumption_growth)-1;
    arx.real_household_consumption_growth=[repmat(data.real_household_consumption_growth(data.years_num==year_num),1,number_seeds);arx.real_household_consumption_growth];
    
    arx.real_household_consumption_growth_quarterly=diff(log([repmat(data.real_household_consumption_quarterly(data.quarters_num==quarter_num),1,number_seeds);real_household_consumption_quarterly]));
    % calculate discrete compounding rate
    arx.real_household_consumption_growth_quarterly=exp(arx.real_household_consumption_growth_quarterly)-1;
    arx.real_household_consumption_growth_quarterly=[repmat(data.real_household_consumption_growth_quarterly(data.quarters_num==quarter_num),1,number_seeds);arx.real_household_consumption_growth_quarterly];
    
    real_fixed_capitalformation_quarterly=data.real_fixed_capitalformation_quarterly(data.quarters_num==quarter_num)*exp(squeeze(V(:,4,:))-Y0(end,4));
    arx.real_fixed_capitalformation_quarterly=[repmat(data.real_fixed_capitalformation_quarterly(data.quarters_num==quarter_num),1,number_seeds);real_fixed_capitalformation_quarterly];
    arx.real_fixed_capitalformation=[repmat(data.real_fixed_capitalformation(data.years_num==year_num),1,number_seeds);toannual(real_fixed_capitalformation_quarterly(5-q:end-mod(q,4),:)')'];
    arx.real_fixed_capitalformation_growth=diff(log([repmat(data.real_fixed_capitalformation(data.years_num==year_num),1,number_seeds);toannual(real_fixed_capitalformation_quarterly(5-q:end-mod(q,4),:)')']));
    % calculate discrete compounding rate
    arx.real_fixed_capitalformation_growth=exp(arx.real_fixed_capitalformation_growth)-1;
    arx.real_fixed_capitalformation_growth=[repmat(data.real_fixed_capitalformation_growth(data.years_num==year_num),1,number_seeds);arx.real_fixed_capitalformation_growth];
    
    arx.real_fixed_capitalformation_growth_quarterly=diff(log([repmat(data.real_fixed_capitalformation_quarterly(data.quarters_num==quarter_num),1,number_seeds);real_fixed_capitalformation_quarterly]));
    % calculate discrete compounding rate
    arx.real_fixed_capitalformation_growth_quarterly=exp(arx.real_fixed_capitalformation_growth_quarterly)-1;
    arx.real_fixed_capitalformation_growth_quarterly=[repmat(data.real_fixed_capitalformation_growth_quarterly(data.quarters_num==quarter_num),1,number_seeds);arx.real_fixed_capitalformation_growth_quarterly];
    
    arx.quarters_num=datenum(datetime(year(datetime(datestr(quarter_num))),month(datetime(datestr(quarter_num)))+(0:3:3*horizon)+1,0))';
    arx.years_num=datenum(year(datetime(datestr(quarter_num)))+1,1:12:horizon/4*12+floor(q/4),0)';
    
    save(['../data/arx/',num2str(year(datetime(datestr(quarters_num(i))))),'Q',num2str(quarter(datetime(datestr(quarters_num(i))))),'.mat'],'arx');
       
end
