function DL_i=search_and_matching_credit(DL_d_i,K_e_i,L_e_i,E_k,zeta,zeta_LTV)
    DL_i=zeros(size(DL_d_i));
    I_FG=find(DL_d_i>0);
    I_FG=I_FG(randperm(length(I_FG)));
    for f=1:length(I_FG)
        i=I_FG(f);
        DL_i(i)=max(0,min(min(DL_d_i(i),zeta_LTV*K_e_i(i)-L_e_i(i)),E_k/zeta-sum(L_e_i+DL_i)));
    end
end

