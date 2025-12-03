#include <iostream>
#include <fstream>
#include <math.h>
#include <time.h>
#include <stdbool.h>   // OK para C y C++
// #include <gsl/gsl_randist.h>
// #include <gsl/gsl_rng.h>
#include <memory>
#include <vector>

// -----------------------------------------------------------------------------
//  CONSTANTES DEL SISTEMA
// -----------------------------------------------------------------------------
#define NCRIT 5
//#define Npart 100       // Raíz del número de partículas totales
#define MAX_NEI 48     // Número máximo de vecinos/
//#define radio_busqueda 0.05


struct celda {
    float xc, yc;           // centro de la celda
    float scell;            // tamaño de la celda
    int NP;                 // número de partículas
    int id_NP[NCRIT + 1];   // índices de partículas
    int level;
    int clave;
    celda* Parent;
  //  celda* nchild[4];
    std::unique_ptr<celda> nchild[4];  

};

struct particula {
    float pos[2];
    float spin;
    celda* CN;
};

struct vecinos_list {
    int nnei;
    int id_nei[MAX_NEI];
};


void init_cell(celda* nc, float xc, float yc, float size) {
    nc->Parent = nullptr;
    nc->xc = xc;
    nc->yc = yc;
    nc->scell = size;
    nc->NP = 0;
    nc->clave = -1;
    nc->level = 1;

    for (int i = 0; i < NCRIT + 1; i++)
        nc->id_NP[i] = -1;

    for (int cuad = 0; cuad < 4; cuad++)
        nc->nchild[cuad] = nullptr;
}

int quad(float x, float y,float xc, float yc){
  int cuad;
  cuad=(x>xc)+((y>yc)<<1); 
  return cuad;
  // |2|3|
  // |0|1|
}
  
void split_cell(celda *C){
  float nsize; //New size
  float n_xc; //New xc
  float n_yc;
  int cuad;
  for(cuad=0;cuad<4;cuad++){
    nsize=C->scell*0.5;
    n_xc= (C->xc) + 0.5*nsize *((cuad & 1 )*2-1);
    n_yc= (C->yc) + 0.5*nsize *((cuad & 2) -1);
//    C->nchild[cuad]= (celda *) calloc(1,sizeof(celda));
    C->nchild[cuad] = std::make_unique<celda>();
    init_cell(C->nchild[cuad].get(),n_xc,n_yc,nsize );
    (C->nchild[cuad])->level=C->level+1;
    C->nchild[cuad]->Parent=C;
  }

}

void imprimir(celda* nodo, particula* Nat) {
    if (nodo != nullptr) {

        std::cout << nodo->xc << " "
                  << nodo->yc << " "
                  << nodo->level << " ";

        if (nodo->Parent != nullptr) {
            std::cout << nodo->Parent->xc << " "
                      << nodo->Parent->yc << " "
                      << nodo->Parent->level << "\n";
        }
        else {
            std::cout << "0.0 0.0 0\n";
        }
    }
    else {
        std::cout << "Nodo Nulo\n";
    }
}





void add_particle(celda *C, particula *at,int j){
  int cuad;
  int cuad0;

  if( (C->NP) == NCRIT ){
    //Siempre divido en cuatro asi no se tengan particulas
    if(C->nchild[0]==NULL){
      split_cell(C);//Se crean los cuatro hijos
    }

    //Las particulas dentro de la celda padre, las 
    //distribuyo a sus nuevos cuadrantes
    for(int l=0;l<NCRIT;l++){
      if(C->id_NP[l] >= 0 ){
	cuad=quad(at[C->id_NP[l]].pos[0],at[C->id_NP[l]].pos[1], C->xc,C->yc);
	add_particle(C->nchild[cuad].get(),at,C->id_NP[l]);
	C->id_NP[l]=-1;
      }
    }
    cuad0=quad(at[j].pos[0],at[j].pos[1],C->xc,C->yc);
    add_particle(C->nchild[cuad0].get(),at,j);
    C->id_NP[NCRIT]= -1;
    C->NP=C->NP+1;    
  }
  else{
    if(C->NP > NCRIT){//El numero de particula mayor que el permitido en la caja
      cuad0=quad(at[j].pos[0],at[j].pos[1],C->xc,C->yc);
      add_particle(C->nchild[cuad0].get(),at,j);
      C->NP=C->NP+1;
      //      C->id_NP[]= -1;
    }
    else{ 
      C->id_NP[C->NP ] = j;
      C->NP    = C->NP+1;
      at[j].CN = C;
    }
  }
}
void preOrden(celda* raiz, particula* Nat) {
    if (raiz != nullptr) {

        // No tener en cuenta el último nivel
        if (raiz->NP > NCRIT) {
            imprimir(raiz, Nat); // Se procesa la raíz

            preOrden(raiz->nchild[0].get(), Nat);
            preOrden(raiz->nchild[1].get(), Nat);
            preOrden(raiz->nchild[2].get(), Nat);
            preOrden(raiz->nchild[3].get(), Nat);
        }
    }
}


void inOrden(celda* raiz, particula* Nat) {
    if (raiz != nullptr) {
        imprimir(raiz, Nat);
        inOrden(raiz->nchild[0].get(), Nat);
    }
}
void postOrden(celda* raiz, particula* Nat) {
    if (raiz != nullptr) {
        
        postOrden(raiz->nchild[0].get(), Nat);
        imprimir(raiz, Nat);

        postOrden(raiz->nchild[1].get(), Nat);
        imprimir(raiz, Nat);

        postOrden(raiz->nchild[2].get(), Nat);
        imprimir(raiz, Nat);

        postOrden(raiz->nchild[3].get(), Nat);
        imprimir(raiz, Nat);
    }
}


bool cell_intersects_circle(celda* C, float x0, float y0, float r) {
    float half = C->scell * 0.5f;

    float dx = std::max(std::fabs(x0 - C->xc) - half, 0.0f);
    float dy = std::max(std::fabs(y0 - C->yc) - half, 0.0f);

    return (dx*dx + dy*dy) <= (r*r);
}
void buscar_vecinos(celda* C,
                    particula* atoms,
                    int id, float r,
                    int* vecinos, int* nvec)
{
    if (C == nullptr) return;

    // Si la celda no intersecta, salimos
    if (!cell_intersects_circle(C,
                                atoms[id].pos[0],
                                atoms[id].pos[1],
                                r))
        return;

    // Si es hoja
    if (!C->nchild[0]) {
        for (int i = 0; i < C->NP; i++) {
            int j = C->id_NP[i];
            if (j == id) continue;

            float dx = atoms[id].pos[0] - atoms[j].pos[0];
            float dy = atoms[id].pos[1] - atoms[j].pos[1];

            if (dx*dx + dy*dy <= r*r) {
                vecinos[*nvec] = j;
                (*nvec)++;
            }
        }
    }
    else {
        // recorrer hijos recursivamente
        for (int k = 0; k < 4; k++) {
            if (C->nchild[k])
                buscar_vecinos(C->nchild[k].get(),
                               atoms, id, r,
                               vecinos, nvec);
        }
    }
}

void export_all_neighbors1(const std::string& filename,
                            vecinos_list* neigh,
                            particula* atomo,
                            int NP)
{
    std::ofstream fout(filename);
    if (!fout) {
        std::cerr << "Error abriendo archivo: " << filename << "\n";
        return;
    }

    fout << "# id  id_vecinos...\n";

    for (int i = 0; i < NP; i++) {
        fout << i;
        for (int k = 0; k < neigh[i].nnei; k++)
            fout << " " << neigh[i].id_nei[k];
        fout << "\n";
    }

    std::cout << "Archivo global de vecinos generado: "
              << filename << "\n";
}

void export_neighbors(const std::string& filename,
                      particula* atomo,
                      int id,
                      int* vecinos,
                      int nvec)
{
    std::ofstream fout(filename);
    if (!fout) {
        std::cerr << "Error abriendo archivo: " << filename << "\n";
        return;
    }

    fout << "# id_particula " << id << "\n";
    fout << "# x_central y_central\n";
    fout << atomo[id].pos[0] << " "
         << atomo[id].pos[1] << "\n";

    fout << "# nvecinos " << nvec << "\n";
    fout << "# id_vecino x_vecino y_vecino dx dy\n";

    for (int i = 0; i < nvec; i++) {
        int j = vecinos[i];
        float dx = atomo[id].pos[0] - atomo[j].pos[0];
        float dy = atomo[id].pos[1] - atomo[j].pos[1];

        fout << j << " "
             << atomo[j].pos[0] << " "
             << atomo[j].pos[1] << " "
             << dx << " "
             << dy << "\n";
    }

    std::cout << "Archivo de vecinos exportado: "
              << filename << "\n";
}



class NeighborSearch {
public:

    NeighborSearch(std::vector<particula>& atoms, float domain_size)
        : atoms(atoms)
    {
        root = std::make_unique<celda>();
        init_cell(root.get(), domain_size/2, domain_size/2, domain_size);
    }

    void build_tree() {
        for (int i = 0; i < atoms.size(); i++) {
            add_particle(root.get(), atoms.data(), i);
        }
    }

    std::vector<int> neighbors_of(int id, float r) const {

        int tmp_ids[MAX_NEI];
        int n = 0;

        buscar_vecinos(root.get(),
                       atoms.data(),
                       id,
                       r,
                       tmp_ids,
                       &n);

        return std::vector<int>(tmp_ids, tmp_ids + n);
    }
    celda* root_ptr() const {
        return root.get();
    }




private:
    std::vector<particula>& atoms;
    std::unique_ptr<celda> root;
};
